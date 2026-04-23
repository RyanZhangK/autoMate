"""Linear integration."""
from __future__ import annotations
from .base import BaseIntegration

API = "https://api.linear.app/graphql"


class LinearIntegration(BaseIntegration):
    name = "linear"
    label = "Linear"
    env_vars = {
        "LINEAR_API_KEY": "API key from linear.app/settings/api",
    }

    def _auth(self) -> dict:
        return {"Authorization": self.env("LINEAR_API_KEY")}

    def _gql(self, query: str, variables: dict | None = None) -> dict:
        return self.post(API, {"query": query, "variables": variables or {}}, self._auth())

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def linear_create_issue(team_id: str, title: str, description: str = "", priority: int = 0) -> str:
            """
            Create a Linear issue.

            Args:
                team_id: Linear team ID (get from linear_list_teams).
                title: Issue title.
                description: Issue description (Markdown).
                priority: 0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low.
            """
            mutation = """
            mutation CreateIssue($input: IssueCreateInput!) {
              issueCreate(input: $input) {
                success
                issue { id identifier title url }
              }
            }
            """
            variables = {"input": {"teamId": team_id, "title": title, "description": description, "priority": priority}}
            r = integration._gql(mutation, variables)
            issue = r.get("data", {}).get("issueCreate", {}).get("issue", {})
            return integration.ok({"id": issue.get("id"), "identifier": issue.get("identifier"), "url": issue.get("url")})

        @mcp.tool()
        def linear_list_issues(team_id: str = "", state: str = "") -> str:
            """
            List Linear issues.

            Args:
                team_id: Optional team ID to filter by.
                state: Optional state filter ("Todo", "In Progress", "Done", etc.).
            """
            filter_parts = []
            if team_id:
                filter_parts.append(f'team: {{id: {{eq: "{team_id}"}}}}')
            if state:
                filter_parts.append(f'state: {{name: {{eq: "{state}"}}}}')
            filter_str = "{" + ", ".join(filter_parts) + "}" if filter_parts else ""
            query = f"""
            query {{
              issues(filter: {filter_str} first: 20) {{
                nodes {{ id identifier title state {{ name }} priority url }}
              }}
            }}
            """
            r = integration._gql(query)
            issues = r.get("data", {}).get("issues", {}).get("nodes", [])
            lines = [f"Found {len(issues)} issue(s):"]
            for i in issues:
                state_name = i.get("state", {}).get("name", "?")
                lines.append(f"  [{i.get('identifier')}] [{state_name}] {i.get('title')} — {i.get('url')}")
            return "\n".join(lines)

        @mcp.tool()
        def linear_list_teams() -> str:
            """List all Linear teams in the workspace."""
            query = "{ teams { nodes { id name key } } }"
            r = integration._gql(query)
            teams = r.get("data", {}).get("teams", {}).get("nodes", [])
            lines = [f"Found {len(teams)} team(s):"]
            for t in teams:
                lines.append(f"  [{t.get('key')}] {t.get('name')} — {t.get('id')}")
            return "\n".join(lines)

        @mcp.tool()
        def linear_update_issue(issue_id: str, state_id: str = "", title: str = "", description: str = "") -> str:
            """
            Update a Linear issue.

            Args:
                issue_id: Linear issue ID.
                state_id: New workflow state ID (optional).
                title: New title (optional).
                description: New description (optional).
            """
            input_data: dict = {}
            if state_id:
                input_data["stateId"] = state_id
            if title:
                input_data["title"] = title
            if description:
                input_data["description"] = description
            mutation = """
            mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
              issueUpdate(id: $id, input: $input) {
                success
                issue { id identifier title }
              }
            }
            """
            r = integration._gql(mutation, {"id": issue_id, "input": input_data})
            issue = r.get("data", {}).get("issueUpdate", {}).get("issue", {})
            return integration.ok({"id": issue.get("id"), "identifier": issue.get("identifier"), "title": issue.get("title")})
