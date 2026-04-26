"""GitLab integration."""
from __future__ import annotations
import urllib.parse
from .base import BaseIntegration


class GitLabIntegration(BaseIntegration):
    name = "gitlab"
    label = "GitLab"
    env_vars = {
        "GITLAB_TOKEN": "Personal access token from gitlab.com/-/profile/personal_access_tokens",
        "GITLAB_BASE_URL": "GitLab instance URL (default https://gitlab.com)",
    }

    def is_configured(self) -> bool:
        import os
        return bool(os.environ.get("GITLAB_TOKEN"))

    def _api(self, path: str) -> str:
        base = self.env("GITLAB_BASE_URL").rstrip("/") or "https://gitlab.com"
        return f"{base}/api/v4{path}"

    def _auth(self) -> dict:
        return {"PRIVATE-TOKEN": self.env("GITLAB_TOKEN")}

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def gitlab_create_issue(project_id: str, title: str, description: str = "", labels: str = "") -> str:
            """
            Create a GitLab issue.

            Args:
                project_id: Project ID or URL-encoded namespace/project (e.g. "mygroup%2Fmyproject").
                title: Issue title.
                description: Issue description (Markdown).
                labels: Comma-separated label names.
            """
            data: dict = {"title": title, "description": description}
            if labels:
                data["labels"] = labels
            r = integration.post(integration._api(f"/projects/{project_id}/issues"), data, integration._auth())
            return integration.ok({"iid": r.get("iid"), "url": r.get("web_url")})

        @mcp.tool()
        def gitlab_list_issues(project_id: str, state: str = "opened", limit: int = 20) -> str:
            """
            List GitLab issues for a project.

            Args:
                project_id: Project ID or URL-encoded path.
                state: "opened", "closed", or "all".
                limit: Max issues (default 20).
            """
            params = urllib.parse.urlencode({"state": state, "per_page": limit})
            r = integration.get(integration._api(f"/projects/{project_id}/issues?{params}"), integration._auth())
            issues = r if isinstance(r, list) else []
            lines = [f"{len(issues)} issue(s) [{state}]:"]
            for i in issues:
                lines.append(f"  #{i['iid']} {i['title']} — {i['web_url']}")
            return "\n".join(lines)

        @mcp.tool()
        def gitlab_create_mr(project_id: str, title: str, source_branch: str, target_branch: str = "main", description: str = "") -> str:
            """
            Create a GitLab merge request.

            Args:
                project_id: Project ID or URL-encoded path.
                title: MR title.
                source_branch: Source branch name.
                target_branch: Target branch name (default "main").
                description: MR description (Markdown).
            """
            r = integration.post(
                integration._api(f"/projects/{project_id}/merge_requests"),
                {"title": title, "source_branch": source_branch, "target_branch": target_branch, "description": description},
                integration._auth(),
            )
            return integration.ok({"iid": r.get("iid"), "url": r.get("web_url")})

        @mcp.tool()
        def gitlab_get_project(project_id: str) -> str:
            """
            Get GitLab project info.

            Args:
                project_id: Project ID or URL-encoded namespace/project.
            """
            r = integration.get(integration._api(f"/projects/{project_id}"), integration._auth())
            return integration.ok({
                "name": r.get("name_with_namespace"),
                "description": r.get("description"),
                "stars": r.get("star_count"),
                "forks": r.get("forks_count"),
                "open_issues": r.get("open_issues_count"),
                "url": r.get("web_url"),
            })

        @mcp.tool()
        def gitlab_list_pipelines(project_id: str, limit: int = 10) -> str:
            """
            List recent CI/CD pipelines for a GitLab project.

            Args:
                project_id: Project ID or URL-encoded path.
                limit: Max pipelines to return (default 10).
            """
            params = urllib.parse.urlencode({"per_page": limit})
            r = integration.get(integration._api(f"/projects/{project_id}/pipelines?{params}"), integration._auth())
            pipelines = r if isinstance(r, list) else []
            lines = [f"{len(pipelines)} pipeline(s):"]
            for p in pipelines:
                lines.append(f"  #{p['id']} [{p['status']}] {p['ref']} — {p.get('web_url')}")
            return "\n".join(lines)
