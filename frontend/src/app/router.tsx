import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LandingPage } from "@/pages/landing-page";
import { IdeaWorkspacePage } from "@/pages/idea-workspace";
import ReviewPage from "@/pages/review-page";
import AdminPanel from "@/pages/admin-panel";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/idea/:id" element={<IdeaWorkspacePage />} />
        <Route path="/reviews" element={<ReviewPage />} />
        <Route path="/admin" element={<AdminPanel />} />
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>
    </BrowserRouter>
  );
}
