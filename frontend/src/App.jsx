import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import BrandKit from "./pages/BrandKit";
import NewContent from "./pages/NewContent";
import ContentReview from "./pages/ContentReview";
import Insights from "./pages/Insights";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="flex gap-6 p-4 border-b bg-white items-center">
        <span className="font-bold text-lg">Vouch</span>
        <Link to="/brand-kit" className="text-sm font-medium">Brand Kit</Link>
        <Link to="/new" className="text-sm font-medium">New Content</Link>
        <Link to="/insights" className="text-sm font-medium">Insights</Link>
      </nav>
      <Routes>
        <Route path="/" element={<NewContent />} />
        <Route path="/brand-kit" element={<BrandKit />} />
        <Route path="/new" element={<NewContent />} />
        <Route path="/content/:id" element={<ContentReview />} />
        <Route path="/insights" element={<Insights />} />
      </Routes>
    </BrowserRouter>
  );
}