import { useAuth } from "../app/auth";
import { Layout } from "../shared/ui/Layout";
import { Card } from "../shared/ui/Card";
import { Empty } from "../shared/ui/States";

// Replace with the task's user screens. Users see only their own data.
export function UserHome() {
  const { user, logout } = useAuth();
  return (
    <Layout title="내 정보" user={user?.user_id} onLogout={logout}>
      <Card title="조회">
        <Empty message="조회할 날짜를 선택하세요." />
      </Card>
    </Layout>
  );
}
