def has_been_submitted(project_id: str) -> bool:
    """True if a BRD version exists for this project, meaning it was submitted at least once."""
    from apps.review.models import BrdVersion

    return BrdVersion.objects.filter(project_id=project_id).exists()
