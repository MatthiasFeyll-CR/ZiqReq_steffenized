import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthenticatedLayout } from "@/components/layout/AuthenticatedLayout";
import { LandingPage } from "@/pages/landing-page";
import { IdeaWorkspacePage } from "@/pages/idea-workspace";
import ReviewPage from "@/pages/review-page";
import AdminPanel from "@/pages/admin-panel";
import LoginPage from "@/pages/login-page";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<AuthenticatedLayout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/idea/:id" element={<IdeaWorkspacePage />} />
          <Route path="/reviews" element={<ReviewPage />} />
          <Route path="/admin" element={<AdminPanel />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
