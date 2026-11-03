import { Component, ReactNode } from "react";
import { ErrorBox } from "../shared/ui/States";

export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    if (this.state.failed) {
      return <ErrorBox message="화면을 표시하는 중 문제가 생겼습니다." action={<a href="/">처음으로</a>} />;
    }
    return this.props.children;
  }
}
