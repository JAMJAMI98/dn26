from app.core.errors import AppError, require_fields
from app.infrastructure import auth_repo
from app.presentation.deps import bearer_token, login_required
from app.presentation.http import Response


def register(router, settings):
    @router.route("POST", "/api/auth/login")
    def login(req):
        body = require_fields(req.json(), {"id": str, "password": str})
        user = auth_repo.authenticate(body["id"], body["password"])
        if not user:
            raise AppError(401, "invalid_credentials", "아이디 또는 비밀번호가 올바르지 않습니다.")
        s = auth_repo.create_session(user, settings.session_ttl_min)
        return Response(200, {"token": s["token"], "user_id": user["id"], "role": user["role"], "expires_at": s["expires_at"]})

    @router.route("POST", "/api/auth/logout")
    def logout(req):
        auth_repo.delete_session(bearer_token(req))
        return Response(204)

    @router.route("GET", "/api/auth/me")
    @login_required
    def me(req):
        return Response(200, {"user_id": req.user["id"], "role": req.user["role"]})
