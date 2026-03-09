import { BrowserRouter, Routes, Route } from "react-router-dom";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<div>ZiqReq — Landing Page</div>} />
        <Route path="/ideas/:id" element={<div>Idea Workspace</div>} />
        <Route path="/reviews" element={<div>Review Page</div>} />
        <Route path="/admin" element={<div>Admin Panel</div>} />
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>
    </BrowserRouter>
  );
}
