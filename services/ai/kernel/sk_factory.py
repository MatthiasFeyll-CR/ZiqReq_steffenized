"""Semantic Kernel kernel construction with Azure OpenAI connector."""

from __future__ import annotations

import logging

from django.conf import settings
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

logger = logging.getLogger(__name__)


def create_kernel(
    deployment_name: str,
    service_id: str = "default",
) -> Kernel:
    """Create an SK Kernel wired to an Azure OpenAI deployment.

    Args:
        deployment_name: The Azure OpenAI deployment to use.
        service_id: Logical service identifier within the kernel.

    Returns:
        Configured Kernel instance ready for agent use.
    """
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    api_key = settings.AZURE_OPENAI_API_KEY
    api_version = settings.AZURE_OPENAI_API_VERSION

    if not endpoint or not api_key:
        raise ValueError(
            "AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set"
        )

    kernel = Kernel()
    kernel.add_service(
        AzureChatCompletion(
            service_id=service_id,
            deployment_name=deployment_name,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
    )

    logger.info(
        "SK Kernel created: service_id=%s, deployment=%s",
        service_id,
        deployment_name,
    )
    return kernel
