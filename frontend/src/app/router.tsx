import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LandingPage } from "@/pages/landing-page";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/idea/:id" element={<div>Idea Workspace</div>} />
        <Route path="/reviews" element={<div>Review Page</div>} />
        <Route path="/admin" element={<div>Admin Panel</div>} />
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>
    </BrowserRouter>
  );
}
