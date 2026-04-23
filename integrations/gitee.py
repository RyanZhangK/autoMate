"""Gitee (码云) integration — China's GitHub alternative."""
from __future__ import annotations
from .base import BaseIntegration

API = "https://gitee.com/api/v5"


class GiteeIntegration(BaseIntegration):
    name = "gitee"
    label = "Gitee (码云)"
    env_vars = {
        "GITEE_ACCESS_TOKEN": "Personal access token from gitee.com/profile/personal_access_tokens",
    }

    def _auth(self) -> dict:
        return {"Authorization": f"token {self.env('GITEE_ACCESS_TOKEN')}"}

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def gitee_create_issue(owner: str, repo: str, title: str, body: str = "", labels: str = "") -> str:
            """
            Create a Gitee issue.

            Args:
                owner: Repository owner (username or org).
                repo: Repository name.
                title: Issue title.
                body: Issue body (Markdown).
                labels: Comma-separated label names.
            """
            data: dict = {"access_token": integration.env("GITEE_ACCESS_TOKEN"), "title": title, "body": body}
            if labels:
                data["labels"] = labels
            r = integration.post(f"{API}/repos/{owner}/{repo}/issues", data, integration._auth())
            return integration.ok({"number": r.get("number"), "url": r.get("html_url")})

        @mcp.tool()
        def gitee_list_issues(owner: str, repo: str, state: str = "open", limit: int = 20) -> str:
            """
            List Gitee issues for a repository.

            Args:
                owner: Repository owner.
                repo: Repository name.
                state: "open", "closed", or "all".
                limit: Max issues to return (default 20).
            """
            import urllib.parse
            params = urllib.parse.urlencode({
                "access_token": integration.env("GITEE_ACCESS_TOKEN"),
                "state": state, "per_page": limit,
            })
            r = integration.get(f"{API}/repos/{owner}/{repo}/issues?{params}", integration._auth())
            issues = r if isinstance(r, list) else []
            lines = [f"{len(issues)} issue(s) [{state}] in {owner}/{repo}:"]
            for i in issues:
                lines.append(f"  #{i['number']} {i['title']} — {i['html_url']}")
            return "\n".join(lines)

        @mcp.tool()
        def gitee_get_repo(owner: str, repo: str) -> str:
            """
            Get Gitee repository info.

            Args:
                owner: Repository owner.
                repo: Repository name.
            """
            import urllib.parse
            params = urllib.parse.urlencode({"access_token": integration.env("GITEE_ACCESS_TOKEN")})
            r = integration.get(f"{API}/repos/{owner}/{repo}?{params}", integration._auth())
            return integration.ok({
                "name": r.get("full_name"),
                "description": r.get("description"),
                "stars": r.get("stargazers_count"),
                "forks": r.get("forks_count"),
                "open_issues": r.get("open_issues_count"),
                "language": r.get("language"),
                "url": r.get("html_url"),
            })

        @mcp.tool()
        def gitee_create_pr(owner: str, repo: str, title: str, head: str, base: str = "master", body: str = "") -> str:
            """
            Create a Gitee pull request.

            Args:
                owner: Repository owner.
                repo: Repository name.
                title: PR title.
                head: Source branch name.
                base: Target branch name (default "master").
                body: PR description.
            """
            r = integration.post(
                f"{API}/repos/{owner}/{repo}/pulls",
                {"access_token": integration.env("GITEE_ACCESS_TOKEN"), "title": title, "head": head, "base": base, "body": body},
                integration._auth(),
            )
            return integration.ok({"number": r.get("number"), "url": r.get("html_url")})
