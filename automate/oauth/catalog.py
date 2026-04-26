"""OAuth provider catalog.

Authorization-code flow only. Each spec is the minimum the server needs to
build the consent URL and exchange the callback code for a token.

The actual ``client_id`` / ``client_secret`` for the user's installed instance
of autoMate live in the ``connections`` table (``metadata`` field) and are
populated through the Settings → "Register OAuth app" wizard. We document the
URL where the user creates an OAuth app for each provider so the wizard can
deep-link them there.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthSpec:
    id: str                       # connection id, matches integrations/<id>.py
    display_name: str
    authorize_url: str
    token_url: str
    scopes: tuple[str, ...]
    register_app_url: str         # where the user goes to create their OAuth app
    docs_url: str
    extra_auth_params: dict       # provider-specific quirks (e.g. owner=user)
    token_field: str = "access_token"
    refresh_field: str | None = "refresh_token"


OAUTH_PROVIDERS: tuple[OAuthSpec, ...] = (
    OAuthSpec(
        id="github",
        display_name="GitHub",
        authorize_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        scopes=("repo", "read:user", "read:org"),
        register_app_url="https://github.com/settings/applications/new",
        docs_url="https://docs.github.com/en/apps/oauth-apps",
        extra_auth_params={},
    ),
    OAuthSpec(
        id="notion",
        display_name="Notion",
        authorize_url="https://api.notion.com/v1/oauth/authorize",
        token_url="https://api.notion.com/v1/oauth/token",
        scopes=(),
        register_app_url="https://www.notion.so/my-integrations",
        docs_url="https://developers.notion.com/docs/authorization",
        extra_auth_params={"owner": "user"},
    ),
    OAuthSpec(
        id="slack",
        display_name="Slack",
        authorize_url="https://slack.com/oauth/v2/authorize",
        token_url="https://slack.com/api/oauth.v2.access",
        scopes=("chat:write", "channels:read", "users:read"),
        register_app_url="https://api.slack.com/apps",
        docs_url="https://api.slack.com/authentication/oauth-v2",
        extra_auth_params={},
    ),
    OAuthSpec(
        id="linear",
        display_name="Linear",
        authorize_url="https://linear.app/oauth/authorize",
        token_url="https://api.linear.app/oauth/token",
        scopes=("read", "write"),
        register_app_url="https://linear.app/settings/api/applications/new",
        docs_url="https://developers.linear.app/docs/oauth/authentication",
        extra_auth_params={},
    ),
    OAuthSpec(
        id="feishu",
        display_name="飞书 / Lark",
        authorize_url="https://open.feishu.cn/open-apis/authen/v1/index",
        token_url="https://open.feishu.cn/open-apis/authen/v2/oauth/token",
        scopes=(),
        register_app_url="https://open.feishu.cn/app",
        docs_url="https://open.feishu.cn/document/server-docs/authentication-management/access-token/web-app-access-token",
        extra_auth_params={},
    ),
    OAuthSpec(
        id="dingtalk",
        display_name="钉钉",
        authorize_url="https://login.dingtalk.com/oauth2/auth",
        token_url="https://api.dingtalk.com/v1.0/oauth2/userAccessToken",
        scopes=("openid",),
        register_app_url="https://open-dev.dingtalk.com/fe/app",
        docs_url="https://open.dingtalk.com/document/orgapp/obtain-identity-credentials",
        extra_auth_params={"prompt": "consent"},
    ),
)


def get_oauth_spec(id: str) -> OAuthSpec | None:
    return next((p for p in OAUTH_PROVIDERS if p.id == id), None)
