"""One error shape for every API failure: {"code", "message", "details"}. Internal errors never leak."""


class AppError(Exception):
    def __init__(self, status: int, code: str, message: str, details=None):
        super().__init__(message)
        self.status, self.code, self.message, self.details = status, code, message, details


def body(code: str, message: str, details=None) -> dict:
    return {"code": code, "message": message, "details": details}


def require_fields(data, spec: dict) -> dict:
    """Validate a JSON object: spec = {"field": type}. Raises 422 invalid_input with per-field details."""
    if not isinstance(data, dict):
        raise AppError(422, "invalid_input", "입력이 올바르지 않습니다.", [{"field": "body", "reason": "JSON 객체가 필요합니다."}])
    details = []
    for name, typ in spec.items():
        v = data.get(name)
        if v is None or (isinstance(v, str) and not v.strip()):
            details.append({"field": name, "reason": "필수 값입니다."})
        elif not isinstance(v, typ) or isinstance(v, bool) and typ is not bool:
            details.append({"field": name, "reason": f"{typ.__name__} 형식이어야 합니다."})
    if details:
        raise AppError(422, "invalid_input", "입력이 올바르지 않습니다.", details)
    return data
