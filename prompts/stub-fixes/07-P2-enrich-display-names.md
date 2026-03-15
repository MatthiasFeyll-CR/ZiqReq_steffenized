# P2: enrich_with_display_names — UUID to Display Name Resolution

## Goal

The `enrich_with_display_names` utility is stubbed and always returns an empty dict. Any feature that needs to resolve user UUIDs to human-readable display names gets nothing back, causing UUIDs or empty strings to appear in the UI instead of names.

This affects: multi-user chat (showing who sent messages), collaborator lists, review timeline entries, presence indicators, and notification content.

## Files to Modify

### Primary file:
- `services/gateway/grpc_clients/enrichment.py`
  ```python
  def enrich_with_display_names(user_ids: list[str]) -> dict[str, str]:
      """Resolve a list of user UUIDs to display names.
      Stub returns empty dict; full implementation queries the users table.
      """
      logger.warning("enrich_with_display_names stub called")
      return {}
  ```

### User model / table:
- Search for the User model. Check:
  - `services/gateway/apps/authentication/` — likely contains the user model or references Django's auth user
  - `services/core/apps/` — may have a custom user model
  - The app uses dev auth bypass with 4 preconfigured users (F-7.1), so check `services/gateway/apps/authentication/views.py` for how users are stored

### Dev user switcher (for context on user storage):
- `frontend/src/components/auth/DevUserSwitcher.tsx` line 26 says:
  ```typescript
  // Fallback: use hardcoded dev users if API not available
  ```
  Check what API endpoint provides user data

## Implementation

```python
def enrich_with_display_names(user_ids: list[str]) -> dict[str, str]:
    """Resolve a list of user UUIDs to display names."""
    if not user_ids:
        return {}

    # Query the users table for matching IDs
    # Adjust model import and field names based on actual User model
    from apps.authentication.models import User  # or wherever the User model lives

    users = User.objects.filter(id__in=user_ids).values_list("id", "display_name")
    return {str(uid): name for uid, name in users}
```

If the User model uses `first_name` + `last_name` instead of `display_name`:
```python
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(id__in=user_ids)
    return {str(u.id): f"{u.first_name} {u.last_name}".strip() or u.email for u in users}
```

## Callers of This Function

Search the codebase for `enrich_with_display_names` imports to find all call sites. Each caller passes a list of user UUIDs and expects back a `{uuid: "Display Name"}` mapping.

## Related Requirements

- **F-2.5:** Multi-User Awareness — AI detects which user sent each message, addresses users by name when multiple users collaborate
- **F-6.3:** Presence Tracking — Online user indicators with names
- **F-8.4:** Collaborator Management — shows collaborator names
- **F-4.6:** Review timeline — shows commenter names
