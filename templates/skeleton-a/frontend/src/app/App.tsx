import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import { RequireRole } from "./RequireRole";
import { ErrorBoundary } from "./ErrorBoundary";
import { LoginPage } from "../pages/LoginPage";
import { ForbiddenPage } from "../pages/ForbiddenPage";
import { AdminHome } from "../pages/AdminHome";
import { UserHome } from "../pages/UserHome";

function RoleHome() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === "admin" ? "/admin" : "/me"} replace />;
}

export function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/403" element={<ForbiddenPage />} />
          <Route path="/admin/*" element={<RequireRole roles={["admin"]}><AdminHome /></RequireRole>} />
          <Route path="/me/*" element={<RequireRole roles={["user"]}><UserHome /></RequireRole>} />
          <Route path="*" element={<RoleHome />} />
        </Routes>
      </AuthProvider>
    </ErrorBoundary>
  );
}
