import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthenticatedLayout } from "@/components/layout/AuthenticatedLayout";
import { LandingPage } from "@/pages/landing-page";
import { ProjectWorkspacePage } from "@/pages/project-workspace";
import ReviewPage from "@/pages/review-page";
import AdminPanel from "@/pages/admin-panel";
import LoginPage from "@/pages/login-page";
import NotFoundPage from "@/pages/not-found";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<AuthenticatedLayout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/project/:id" element={<ProjectWorkspacePage />} />
          <Route path="/reviews" element={<ReviewPage />} />
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
