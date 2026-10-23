import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function NewContent() {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const navigate = useNavigate();

  const createContent = async () => {
    const res = await api.post("/api/content/", { title, text });
    navigate(`/content/${res.data.content.id}`);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">New Content</h1>
      <input
        className="border p-2 rounded w-full mb-3"
        placeholder="Title (e.g. Instagram Caption)"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <textarea
        className="border p-2 rounded w-full mb-3"
        rows={10}
        placeholder="Paste your content here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        onClick={createContent}
        disabled={!title || !text}
        className="bg-black text-white px-4 py-2 rounded disabled:opacity-50"
      >
        Create & Review
      </button>
    </div>
  );
}