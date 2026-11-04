import { Card, Empty, Layout } from "../shared/ui/components.js";
import { logout } from "../app/auth.js";

// Replace with the task's admin screens (blocks from docs/05 screen spec -> entities/ modules).
export function AdminHome({ navigate, user }) {
  return Layout({ title: "운영", user: user.user_id, onLogout: async () => { await logout(); navigate("/login", { replace: true }); } },
    Card("시작", Empty("데이터를 적용하고 결과를 생성하세요.")));
}
