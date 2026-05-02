import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "@/components/Layout";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Employees from "@/pages/Employees";
import EmployeeDetail from "@/pages/EmployeeDetail";
import Predict from "@/pages/Predict";
import ModelManagement from "@/pages/ModelManagement";
import AuditLog from "@/pages/AuditLog";
import Users from "@/pages/Users";
import { getUser } from "@/lib/api";

function Protected({ children }: { children: JSX.Element }) {
  return getUser() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <Protected>
            <Layout />
          </Protected>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/employees" element={<Employees />} />
        <Route path="/employees/:id" element={<EmployeeDetail />} />
        <Route path="/predict" element={<Predict />} />
        <Route path="/models" element={<ModelManagement />} />
        <Route path="/audit" element={<AuditLog />} />
        <Route path="/users" element={<Users />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
