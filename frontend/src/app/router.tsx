import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LandingPage } from "@/pages/landing-page";
import { IdeaWorkspacePage } from "@/pages/idea-workspace";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/idea/:id" element={<IdeaWorkspacePage />} />
        <Route path="/reviews" element={<div>Review Page</div>} />
        <Route path="/admin" element={<div>Admin Panel</div>} />
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>
    </BrowserRouter>
  );
}
