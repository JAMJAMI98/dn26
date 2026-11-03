import { ReactNode } from "react";

export function Badge({ tone, children }: { tone?: "ok" | "warn" | "danger"; children: ReactNode }) {
  return <span className="ui-badge" data-tone={tone}>{children}</span>;
}
