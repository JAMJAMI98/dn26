import { ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { Button } from "./Button";

export function Layout({ title, nav = [], user, onLogout, children }: {
  title: string;
  nav?: { to: string; label: string }[];
  user?: string;
  onLogout?: () => void;
  children: ReactNode;
}) {
  return (
    <div className="ui-layout">
      <header className="ui-header">
        <h1>{title}</h1>
        <nav className="ui-nav">{nav.map((n) => <NavLink key={n.to} to={n.to}>{n.label}</NavLink>)}</nav>
        {user && <span>{user}</span>}
        {onLogout && <Button onClick={onLogout}>로그아웃</Button>}
      </header>
      <main className="ui-main">{children}</main>
    </div>
  );
}
