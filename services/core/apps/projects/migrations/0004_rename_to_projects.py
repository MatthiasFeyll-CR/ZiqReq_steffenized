"""Rename ideas → projects, idea_collaborators → project_collaborators,
idea_id → project_id in all related tables, and add project_type column."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0003_remove_board"),
    ]

    operations = [
        # ── Rename main tables ──
        migrations.RunSQL(
            sql="ALTER TABLE ideas RENAME TO projects;",
            reverse_sql="ALTER TABLE projects RENAME TO ideas;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE idea_collaborators RENAME TO project_collaborators;",
            reverse_sql="ALTER TABLE project_collaborators RENAME TO idea_collaborators;",
        ),

        # ── Rename indexes on projects (was ideas) ──
        migrations.RunSQL(
            sql="ALTER INDEX idx_ideas_owner RENAME TO idx_projects_owner;",
            reverse_sql="ALTER INDEX idx_projects_owner RENAME TO idx_ideas_owner;",
        ),
        migrations.RunSQL(
            sql="ALTER INDEX idx_ideas_state RENAME TO idx_projects_state;",
            reverse_sql="ALTER INDEX idx_projects_state RENAME TO idx_ideas_state;",
        ),
        migrations.RunSQL(
            sql="ALTER INDEX idx_ideas_deleted_at RENAME TO idx_projects_deleted_at;",
            reverse_sql="ALTER INDEX idx_projects_deleted_at RENAME TO idx_ideas_deleted_at;",
        ),
        migrations.RunSQL(
            sql="ALTER INDEX idx_ideas_state_deleted RENAME TO idx_projects_state_deleted;",
            reverse_sql="ALTER INDEX idx_projects_state_deleted RENAME TO idx_ideas_state_deleted;",
        ),

        # ── Rename indexes on project_collaborators ──
        migrations.RunSQL(
            sql="ALTER INDEX idx_collab_idea RENAME TO idx_collab_project;",
            reverse_sql="ALTER INDEX idx_collab_project RENAME TO idx_collab_idea;",
        ),

        # ── Rename FK columns: idea_id → project_id ──
        migrations.RunSQL(
            sql="ALTER TABLE project_collaborators RENAME COLUMN idea_id TO project_id;",
            reverse_sql="ALTER TABLE project_collaborators RENAME COLUMN project_id TO idea_id;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE chat_messages RENAME COLUMN idea_id TO project_id;",
            reverse_sql="ALTER TABLE chat_messages RENAME COLUMN project_id TO idea_id;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE brd_drafts RENAME COLUMN idea_id TO project_id;",
            reverse_sql="ALTER TABLE brd_drafts RENAME COLUMN project_id TO idea_id;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE brd_versions RENAME COLUMN idea_id TO project_id;",
            reverse_sql="ALTER TABLE brd_versions RENAME COLUMN project_id TO idea_id;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE review_assignments RENAME COLUMN idea_id TO project_id;",
            reverse_sql="ALTER TABLE review_assignments RENAME COLUMN project_id TO idea_id;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE review_timeline_entries RENAME COLUMN idea_id TO project_id;",
            reverse_sql="ALTER TABLE review_timeline_entries RENAME COLUMN project_id TO idea_id;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE collaboration_invitations RENAME COLUMN idea_id TO project_id;",
            reverse_sql="ALTER TABLE collaboration_invitations RENAME COLUMN project_id TO idea_id;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE chat_context_summaries RENAME COLUMN idea_id TO project_id;",
            reverse_sql="ALTER TABLE chat_context_summaries RENAME COLUMN project_id TO idea_id;",
        ),

        # ── Rename idea_comments table and its idea_id column ──
        migrations.RunSQL(
            sql="ALTER TABLE idea_comments RENAME TO project_comments;",
            reverse_sql="ALTER TABLE project_comments RENAME TO idea_comments;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE project_comments RENAME COLUMN idea_id TO project_id;",
            reverse_sql="ALTER TABLE project_comments RENAME COLUMN project_id TO idea_id;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE comment_read_status RENAME COLUMN idea_id TO project_id;",
            reverse_sql="ALTER TABLE comment_read_status RENAME COLUMN project_id TO idea_id;",
        ),

        # ── Rename indexes on related tables ──
        migrations.RunSQL(
            sql="ALTER INDEX idx_comments_idea_ts RENAME TO idx_comments_project_ts;",
            reverse_sql="ALTER INDEX idx_comments_project_ts RENAME TO idx_comments_idea_ts;",
        ),
        migrations.RunSQL(
            sql="ALTER INDEX idx_chat_idea_created RENAME TO idx_chat_project_created;",
            reverse_sql="ALTER INDEX idx_chat_project_created RENAME TO idx_chat_idea_created;",
        ),
        migrations.RunSQL(
            sql="ALTER INDEX idx_brd_ver_idea RENAME TO idx_brd_ver_project;",
            reverse_sql="ALTER INDEX idx_brd_ver_project RENAME TO idx_brd_ver_idea;",
        ),
        migrations.RunSQL(
            sql="ALTER INDEX idx_review_idea RENAME TO idx_review_project;",
            reverse_sql="ALTER INDEX idx_review_project RENAME TO idx_review_idea;",
        ),
        migrations.RunSQL(
            sql="ALTER INDEX idx_timeline_idea RENAME TO idx_timeline_project;",
            reverse_sql="ALTER INDEX idx_timeline_project RENAME TO idx_timeline_idea;",
        ),
        migrations.RunSQL(
            sql="ALTER INDEX idx_invite_idea RENAME TO idx_invite_project;",
            reverse_sql="ALTER INDEX idx_invite_project RENAME TO idx_invite_idea;",
        ),
        migrations.RunSQL(
            sql="ALTER INDEX idx_ctx_summary_idea RENAME TO idx_ctx_summary_project;",
            reverse_sql="ALTER INDEX idx_ctx_summary_project RENAME TO idx_ctx_summary_idea;",
        ),

        # ── Add project_type column with CHECK constraint ──
        migrations.RunSQL(
            sql=(
                "ALTER TABLE projects "
                "ADD COLUMN project_type varchar(20) NOT NULL DEFAULT 'software' "
                "CONSTRAINT projects_project_type_check "
                "CHECK (project_type IN ('software', 'non_software'));"
            ),
            reverse_sql="ALTER TABLE projects DROP COLUMN project_type;",
        ),

        # ── Add index on project_type ──
        migrations.RunSQL(
            sql="CREATE INDEX idx_projects_type ON projects(project_type);",
            reverse_sql="DROP INDEX idx_projects_type;",
        ),
    ]
