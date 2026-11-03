import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../app/auth";
import { Button } from "../shared/ui/Button";
import { Card } from "../shared/ui/Card";
import { Field } from "../shared/ui/Field";
import { ApiError } from "../shared/api/client";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const u = await login(id, password);
      navigate(u.role === "admin" ? "/admin" : "/me", { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "로그인하지 못했습니다. 잠시 후 다시 시도하세요.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="ui-center">
      <div className="ui-narrow">
        <Card title="로그인">
          <form onSubmit={submit} className="ui-form">
            <Field label="아이디" value={id} onChange={(e) => setId(e.target.value)} autoComplete="username" required />
            <Field label="비밀번호" type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password" required error={error ?? undefined} />
            <Button variant="primary" type="submit" disabled={busy}>{busy ? "확인 중…" : "로그인"}</Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
