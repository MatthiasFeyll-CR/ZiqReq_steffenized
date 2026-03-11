import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LandingPage } from "@/pages/landing-page";
import { IdeaWorkspacePage } from "@/pages/idea-workspace";
import ReviewPage from "@/pages/review-page";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/idea/:id" element={<IdeaWorkspacePage />} />
        <Route path="/reviews" element={<ReviewPage />} />
        <Route path="/admin" element={<div>Admin Panel</div>} />
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>
    </BrowserRouter>
  );
}
