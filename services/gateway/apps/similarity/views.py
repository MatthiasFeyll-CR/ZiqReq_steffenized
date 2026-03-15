"""Similarity views are served by the ideas app.

Endpoints:
- GET  /api/ideas/:id/similar         → apps.ideas.views.get_similar_ideas
- POST /api/ideas/:id/merge-request   → apps.ideas.views.create_merge_request
- POST /api/merge-requests/:id/consent → apps.ideas.views.consent_merge_request

This module intentionally has no views. The similarity app provides
models (MergeRequest, IdeaKeywords), services (merge_service, append_service),
and Celery tasks (owned by the Core service).
"""
