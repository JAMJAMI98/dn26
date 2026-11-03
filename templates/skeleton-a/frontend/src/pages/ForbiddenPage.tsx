import { ErrorBox } from "../shared/ui/States";

export function ForbiddenPage() {
  return <ErrorBox message="이 화면을 볼 권한이 없습니다." action={<a href="/">내 첫 화면으로</a>} />;
}
