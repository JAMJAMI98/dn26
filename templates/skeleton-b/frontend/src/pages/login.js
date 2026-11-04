import { h } from "../shared/ui/dom.js";
import { Button, Card, Field } from "../shared/ui/components.js";
import { ApiError } from "../shared/api/client.js";
import { homePath, login } from "../app/auth.js";

export function LoginPage({ navigate }) {
  const error = h("span", { className: "ui-error", role: "alert" });
  const submit = Button("로그인", { variant: "primary", type: "submit" });
  const form = h("form", { className: "ui-form" },
    Field({ label: "아이디", name: "id", autocomplete: "username", required: true }),
    Field({ label: "비밀번호", name: "password", type: "password", autocomplete: "current-password", required: true }),
    error, submit);
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    submit.disabled = true; submit.textContent = "확인 중…"; error.textContent = "";
    try {
      const u = await login(form.elements.id.value, form.elements.password.value);
      navigate(homePath(u), { replace: true });
    } catch (err) {
      error.textContent = err instanceof ApiError ? err.message : "로그인하지 못했습니다. 잠시 후 다시 시도하세요.";
      submit.disabled = false; submit.textContent = "로그인";
    }
  });
  return h("div", { className: "ui-center" }, h("div", { className: "ui-narrow" }, Card("로그인", form)));
}
