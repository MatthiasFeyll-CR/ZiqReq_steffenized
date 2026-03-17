import logging
import os
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from .authentication import MiddlewareAuthentication
from .models import Project, ProjectCollaborator, RequirementsDocumentDraft
from .requirements_serializers import (
    RequirementsChildCreateSerializer,
    RequirementsChildPatchSerializer,
    RequirementsDraftPatchSerializer,
    RequirementsDraftResponseSerializer,
    RequirementsGenerateSerializer,
    RequirementsItemCreateSerializer,
    RequirementsItemPatchSerializer,
    RequirementsReorderSerializer,
    get_child_type,
    get_parent_type,
)

logger = logging.getLogger(__name__)


def _require_auth(request: Request):
    user = request.user
    if user is None or not getattr(user, "id", None):
        return None
    return user


def _unauthorized_response() -> Response:
    return Response(
        {"error": "UNAUTHORIZED", "message": "Authentication required"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


def _get_project_or_error(project_id: str):
    try:
        uuid.UUID(project_id)
    except ValueError:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return None, Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    return project, None


def _check_access(user, project) -> Response | None:
    is_owner = project.owner_id == user.id
    is_collaborator = ProjectCollaborator.objects.filter(
        project_id=project.id, user_id=user.id
    ).exists()
    if not (is_owner or is_collaborator):
        return Response(
            {"error": "ACCESS_DENIED", "message": "You do not have access to this project"},
            status=status.HTTP_403_FORBIDDEN,
        )
    return None


def _get_or_create_draft(project) -> RequirementsDocumentDraft:
    draft, _created = RequirementsDocumentDraft.objects.get_or_create(
        project_id=project.id,
        defaults={
            "structure": [],
            "item_locks": {},
            "allow_information_gaps": False,
            "readiness_evaluation": {},
        },
    )
    return draft


def _broadcast_requirements_updated(project_id: str, structure: list, user_id: str) -> None:
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"project_{project_id}",
                {
                    "type": "requirements_updated",
                    "project_id": project_id,
                    "payload": {
                        "structure": structure,
                        "updated_by": user_id,
                    },
                },
            )
    except Exception:
        logger.exception("Failed to broadcast requirements_updated for project %s", project_id)


# --- GET/PATCH /api/projects/:id/requirements/ ---


@api_view(["GET", "PATCH"])
@authentication_classes([MiddlewareAuthentication])
def requirements_root(request: Request, project_id: str) -> Response:
    if request.method == "PATCH":
        return _patch_requirements(request, project_id)
    return _get_requirements(request, project_id)


def _get_requirements(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    draft = _get_or_create_draft(project)
    serializer = RequirementsDraftResponseSerializer(draft)
    return Response(serializer.data)


def _patch_requirements(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    serializer = RequirementsDraftPatchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    draft = _get_or_create_draft(project)
    update_fields = ["updated_at"]
    validated = serializer.validated_data

    if "title" in validated:
        draft.title = validated["title"]
        update_fields.append("title")
    if "short_description" in validated:
        draft.short_description = validated["short_description"]
        update_fields.append("short_description")

    draft.save(update_fields=update_fields)
    response_serializer = RequirementsDraftResponseSerializer(draft)
    return Response(response_serializer.data)


# --- POST /api/projects/:id/requirements/items ---


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def requirements_items(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    serializer = RequirementsItemCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data
    expected_type = get_parent_type(project.project_type)

    if validated["type"] != expected_type:
        return Response(
            {
                "error": "INVALID_TYPE",
                "message": f"Expected type '{expected_type}' for {project.project_type} projects.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    draft = _get_or_create_draft(project)
    structure = list(draft.structure or [])

    new_item = {
        "id": str(uuid.uuid4()),
        "type": validated["type"],
        "title": validated["title"],
        "description": validated.get("description", ""),
        "children": [],
        "metadata": {},
    }

    structure.append(new_item)
    draft.structure = structure
    draft.save(update_fields=["structure", "updated_at"])

    _broadcast_requirements_updated(str(project.id), structure, str(user.id))

    return Response(new_item, status=status.HTTP_201_CREATED)


# --- PATCH/DELETE /api/projects/:id/requirements/items/:item_id ---


@api_view(["PATCH", "DELETE"])
@authentication_classes([MiddlewareAuthentication])
def requirements_item_detail(request: Request, project_id: str, item_id: str) -> Response:
    if request.method == "DELETE":
        return _delete_item(request, project_id, item_id)
    return _patch_item(request, project_id, item_id)


def _patch_item(request: Request, project_id: str, item_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    serializer = RequirementsItemPatchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    draft = _get_or_create_draft(project)
    structure = list(draft.structure or [])

    found_item = None
    for item in structure:
        if item.get("id") == item_id:
            found_item = item
            break

    if found_item is None:
        return Response(
            {"error": "NOT_FOUND", "message": "Item not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    validated = serializer.validated_data
    if "title" in validated:
        found_item["title"] = validated["title"]
    if "description" in validated:
        found_item["description"] = validated["description"]

    draft.structure = structure
    draft.save(update_fields=["structure", "updated_at"])

    _broadcast_requirements_updated(str(project.id), structure, str(user.id))

    return Response(found_item)


def _delete_item(request: Request, project_id: str, item_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    draft = _get_or_create_draft(project)
    structure = list(draft.structure or [])

    new_structure = [item for item in structure if item.get("id") != item_id]

    if len(new_structure) == len(structure):
        return Response(
            {"error": "NOT_FOUND", "message": "Item not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    draft.structure = new_structure
    draft.save(update_fields=["structure", "updated_at"])

    _broadcast_requirements_updated(str(project.id), new_structure, str(user.id))

    return Response(status=status.HTTP_204_NO_CONTENT)


# --- POST /api/projects/:id/requirements/items/:item_id/children ---


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def requirements_children(request: Request, project_id: str, item_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    serializer = RequirementsChildCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    draft = _get_or_create_draft(project)
    structure = list(draft.structure or [])

    parent_item = None
    for item in structure:
        if item.get("id") == item_id:
            parent_item = item
            break

    if parent_item is None:
        return Response(
            {"error": "NOT_FOUND", "message": "Parent item not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    validated = serializer.validated_data
    child_type = get_child_type(project.project_type)

    new_child = {
        "id": str(uuid.uuid4()),
        "type": child_type,
        "title": validated["title"],
        "description": validated.get("description", ""),
        "metadata": {},
    }

    if child_type == "user_story":
        new_child["acceptance_criteria"] = validated.get("acceptance_criteria", [])
        new_child["priority"] = validated.get("priority", "medium")
    elif child_type == "work_package":
        new_child["deliverables"] = validated.get("deliverables", [])
        new_child["dependencies"] = validated.get("dependencies", [])

    children = list(parent_item.get("children", []))
    children.append(new_child)
    parent_item["children"] = children

    draft.structure = structure
    draft.save(update_fields=["structure", "updated_at"])

    _broadcast_requirements_updated(str(project.id), structure, str(user.id))

    return Response(new_child, status=status.HTTP_201_CREATED)


# --- PATCH/DELETE /api/projects/:id/requirements/items/:item_id/children/:child_id ---


@api_view(["PATCH", "DELETE"])
@authentication_classes([MiddlewareAuthentication])
def requirements_child_detail(
    request: Request, project_id: str, item_id: str, child_id: str
) -> Response:
    if request.method == "DELETE":
        return _delete_child(request, project_id, item_id, child_id)
    return _patch_child(request, project_id, item_id, child_id)


def _patch_child(
    request: Request, project_id: str, item_id: str, child_id: str
) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    serializer = RequirementsChildPatchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    draft = _get_or_create_draft(project)
    structure = list(draft.structure or [])

    parent_item = None
    for item in structure:
        if item.get("id") == item_id:
            parent_item = item
            break

    if parent_item is None:
        return Response(
            {"error": "NOT_FOUND", "message": "Parent item not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    found_child = None
    for child in parent_item.get("children", []):
        if child.get("id") == child_id:
            found_child = child
            break

    if found_child is None:
        return Response(
            {"error": "NOT_FOUND", "message": "Child item not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    validated = serializer.validated_data
    for key in ("title", "description", "acceptance_criteria", "deliverables", "dependencies", "priority"):
        if key in validated:
            found_child[key] = validated[key]

    draft.structure = structure
    draft.save(update_fields=["structure", "updated_at"])

    _broadcast_requirements_updated(str(project.id), structure, str(user.id))

    return Response(found_child)


def _delete_child(
    request: Request, project_id: str, item_id: str, child_id: str
) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    draft = _get_or_create_draft(project)
    structure = list(draft.structure or [])

    parent_item = None
    for item in structure:
        if item.get("id") == item_id:
            parent_item = item
            break

    if parent_item is None:
        return Response(
            {"error": "NOT_FOUND", "message": "Parent item not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    children = list(parent_item.get("children", []))
    new_children = [c for c in children if c.get("id") != child_id]

    if len(new_children) == len(children):
        return Response(
            {"error": "NOT_FOUND", "message": "Child item not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    parent_item["children"] = new_children
    draft.structure = structure
    draft.save(update_fields=["structure", "updated_at"])

    _broadcast_requirements_updated(str(project.id), structure, str(user.id))

    return Response(status=status.HTTP_204_NO_CONTENT)


# --- POST /api/projects/:id/requirements/reorder ---


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def requirements_reorder(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    serializer = RequirementsReorderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    draft = _get_or_create_draft(project)
    structure = list(draft.structure or [])

    item_ids = serializer.validated_data["item_ids"]
    item_map = {item["id"]: item for item in structure if "id" in item}

    # Validate all IDs exist
    for item_id in item_ids:
        if item_id not in item_map:
            return Response(
                {"error": "NOT_FOUND", "message": f"Item {item_id} not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    new_structure = [item_map[iid] for iid in item_ids]

    # Append any items not in the reorder list (safety net)
    reordered_ids = set(item_ids)
    for item in structure:
        if item.get("id") not in reordered_ids:
            new_structure.append(item)

    draft.structure = new_structure
    draft.save(update_fields=["structure", "updated_at"])

    _broadcast_requirements_updated(str(project.id), new_structure, str(user.id))

    response_serializer = RequirementsDraftResponseSerializer(draft)
    return Response(response_serializer.data)


# --- POST /api/projects/:id/requirements/generate ---


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def requirements_generate(request: Request, project_id: str) -> Response:
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    project, error = _get_project_or_error(project_id)
    if error:
        return error

    access_error = _check_access(user, project)
    if access_error:
        return access_error

    if project.state != "open":
        return Response(
            {
                "error": "INVALID_STATE",
                "message": "Requirements generation is only available for projects in 'open' state.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RequirementsGenerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data
    mode = validated["mode"]
    locked_item_ids = validated.get("locked_item_ids", [])

    # Invoke AI service
    try:
        from grpc_clients.ai_client import AiClient

        address = os.environ.get("AI_GRPC_ADDRESS", "localhost:50052")
        ai_client = AiClient(address=address)
        result = ai_client.trigger_requirements_generation(
            project_id=str(project.id),
            mode=mode,
            locked_item_ids=locked_item_ids,
        )
    except Exception:
        logger.exception("AI service call failed for project %s", project_id)
        return Response(
            {"error": "SERVICE_UNAVAILABLE", "message": "AI service is currently unavailable."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Broadcast generating event
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"project_{project.id}",
                {
                    "type": "requirements_generating",
                    "project_id": str(project.id),
                    "payload": {"mode": mode},
                },
            )
    except Exception:
        logger.exception("Failed to broadcast requirements_generating for project %s", project_id)

    return Response(
        {
            "status": "accepted",
            "generation_id": result.get("generation_id", ""),
        },
        status=status.HTTP_202_ACCEPTED,
    )
