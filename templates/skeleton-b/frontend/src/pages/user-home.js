import { Card, Empty, Layout } from "../shared/ui/components.js";
import { logout } from "../app/auth.js";

// Replace with the task's user screens. Users see only their own data.
export function UserHome({ navigate, user }) {
  return Layout({ title: "내 정보", user: user.user_id, onLogout: async () => { await logout(); navigate("/login", { replace: true }); } },
    Card("조회", Empty("조회할 날짜를 선택하세요.")));
}
