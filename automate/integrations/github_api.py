"""GitHub integration."""
from __future__ import annotations
from .base import BaseIntegration

API = "https://api.github.com"


class GitHubIntegration(BaseIntegration):
    name = "github"
    label = "GitHub"
    env_vars = {
        "GITHUB_TOKEN": "Personal Access Token from github.com/settings/tokens",
    }

    def _auth(self) -> dict:
        return {
            "Authorization": f"Bearer {self.env('GITHUB_TOKEN')}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def github_create_issue(owner: str, repo: str, title: str, body: str = "", labels: str = "") -> str:
            """
            Create a GitHub issue.

            Args:
                owner: Repository owner (username or org).
                repo: Repository name.
                title: Issue title.
                body: Issue body (Markdown).
                labels: Comma-separated label names (e.g. "bug,enhancement").
            """
            data: dict = {"title": title, "body": body}
            if labels:
                data["labels"] = [l.strip() for l in labels.split(",")]
            r = integration.post(f"{API}/repos/{owner}/{repo}/issues", data, integration._auth())
            return integration.ok({"number": r.get("number"), "url": r.get("html_url")})

        @mcp.tool()
        def github_list_issues(owner: str, repo: str, state: str = "open", limit: int = 20) -> str:
            """
            List GitHub issues for a repository.

            Args:
                owner: Repository owner.
                repo: Repository name.
                state: "open", "closed", or "all".
                limit: Max issues to return (default 20).
            """
            r = integration.get(
                f"{API}/repos/{owner}/{repo}/issues?state={state}&per_page={limit}",
                integration._auth(),
            )
            lines = [f"{len(r)} issue(s) [{state}] in {owner}/{repo}:"]
            for i in r if isinstance(r, list) else []:
                lines.append(f"  #{i['number']} {i['title']} — {i['html_url']}")
            return "\n".join(lines)

        @mcp.tool()
        def github_create_pr(owner: str, repo: str, title: str, head: str, base: str = "main", body: str = "") -> str:
            """
            Create a GitHub pull request.

            Args:
                owner: Repository owner.
                repo: Repository name.
                title: PR title.
                head: Source branch name.
                base: Target branch name (default "main").
                body: PR description (Markdown).
            """
            r = integration.post(
                f"{API}/repos/{owner}/{repo}/pulls",
                {"title": title, "head": head, "base": base, "body": body},
                integration._auth(),
            )
            return integration.ok({"number": r.get("number"), "url": r.get("html_url")})

        @mcp.tool()
        def github_search_repos(query: str, limit: int = 10) -> str:
            """
            Search GitHub repositories.

            Args:
                query: Search query (e.g. "mcp server language:python stars:>100").
                limit: Max results (default 10).
            """
            import urllib.parse
            r = integration.get(
                f"{API}/search/repositories?q={urllib.parse.quote(query)}&per_page={limit}",
                integration._auth(),
            )
            items = r.get("items", [])
            lines = [f"Found {r.get('total_count', 0)} repos, showing {len(items)}:"]
            for i in items:
                lines.append(f"  ⭐{i['stargazers_count']:>6} {i['full_name']} — {i['description'] or ''}")
            return "\n".join(lines)

        @mcp.tool()
        def github_get_repo(owner: str, repo: str) -> str:
            """
            Get GitHub repository info.

            Args:
                owner: Repository owner.
                repo: Repository name.
            """
            r = integration.get(f"{API}/repos/{owner}/{repo}", integration._auth())
            return integration.ok({
                "name": r.get("full_name"),
                "description": r.get("description"),
                "stars": r.get("stargazers_count"),
                "forks": r.get("forks_count"),
                "open_issues": r.get("open_issues_count"),
                "language": r.get("language"),
                "url": r.get("html_url"),
            })
