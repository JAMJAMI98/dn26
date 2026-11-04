import { h } from "../shared/ui/dom.js";
import { Card, ErrorBox } from "../shared/ui/components.js";
import { currentUser, homePath } from "../app/auth.js";

export function ForbiddenPage() {
  const u = currentUser();
  return h("div", { className: "ui-center" }, h("div", { className: "ui-narrow" },
    Card("권한 없음", ErrorBox("이 화면을 볼 권한이 없습니다."),
      h("a", { href: u ? homePath(u) : "/login", "data-link": true }, "내 화면으로 돌아가기"))));
}
