import { useAuth } from "../app/auth";
import { Layout } from "../shared/ui/Layout";
import { Card } from "../shared/ui/Card";
import { Empty } from "../shared/ui/States";

// Replace with the task's admin screens (blocks from docs/05 screen spec -> entities components).
export function AdminHome() {
  const { user, logout } = useAuth();
  return (
    <Layout title="운영" user={user?.user_id} onLogout={logout}>
      <Card title="시작">
        <Empty message="데이터를 적용하고 결과를 생성하세요." />
      </Card>
    </Layout>
  );
}
