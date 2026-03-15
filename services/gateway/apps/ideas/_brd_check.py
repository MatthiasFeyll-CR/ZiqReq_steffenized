def has_been_submitted(idea_id: str) -> bool:
    """True if a BRD version exists for this idea, meaning it was submitted at least once."""
    from apps.review.models import BrdVersion

    return BrdVersion.objects.filter(idea_id=idea_id).exists()
