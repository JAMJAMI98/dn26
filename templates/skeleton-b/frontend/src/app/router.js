// Client-side routes (History API). Role guard: not logged in -> /login, other role -> /403.
import { mount } from "../shared/ui/dom.js";
import { ErrorBox } from "../shared/ui/components.js";
import { currentUser, homePath, restore } from "./auth.js";
import { LoginPage } from "../pages/login.js";
import { ForbiddenPage } from "../pages/forbidden.js";
import { AdminHome } from "../pages/admin-home.js";
import { UserHome } from "../pages/user-home.js";

// path prefix -> { page, roles }. Add task screens here (one page module per screen).
const ROUTES = [
  { path: "/login", page: LoginPage },
  { path: "/403", page: ForbiddenPage },
  { path: "/admin", page: AdminHome, roles: ["admin"] },
  { path: "/me", page: UserHome, roles: ["user"] },
];

let root;

export function navigate(to, { replace = false } = {}) {
  history[replace ? "replaceState" : "pushState"](null, "", to);
  render();
}

async function render() {
  const path = location.pathname;
  const route = ROUTES.find((r) => path === r.path || path.startsWith(r.path + "/"));
  const user = currentUser();
  if (!route) return navigate(user ? homePath(user) : "/login", { replace: true });
  if (route.roles && !user) return navigate("/login", { replace: true });
  if (route.roles && !route.roles.includes(user.role)) return navigate("/403", { replace: true });
  try {
    mount(root, await route.page({ navigate, user }));
  } catch (e) {
    console.error(e);
    mount(root, ErrorBox("화면을 표시하지 못했습니다. 새로고침해 주세요."));
  }
}

export async function startApp(el) {
  root = el;
  // internal links: <a data-link href="/x"> navigate without reload
  document.addEventListener("click", (e) => {
    const a = e.target.closest("a[data-link]");
    if (a && a.origin === location.origin) { e.preventDefault(); navigate(a.pathname); }
  });
  addEventListener("popstate", render);
  await restore();
  render();
}
