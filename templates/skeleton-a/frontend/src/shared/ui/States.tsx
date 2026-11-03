import { ReactNode } from "react";

// Four states every block shows: first(empty) / loading / error / result.
export function Empty({ message, action }: { message: string; action?: ReactNode }) {
  return <div className="ui-state" data-kind="empty"><p>{message}</p>{action}</div>;
}

export function Loading({ message = "불러오는 중입니다…" }: { message?: string }) {
  return <div className="ui-state" data-kind="loading" role="status">{message}</div>;
}

export function ErrorBox({ message, action }: { message: string; action?: ReactNode }) {
  return <div className="ui-state" data-kind="error" role="alert"><p>{message}</p>{action}</div>;
}
