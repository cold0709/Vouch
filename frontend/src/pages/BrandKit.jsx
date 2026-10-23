import { useState, useEffect } from "react";
import { api } from "../api";

export default function BrandKit() {
  const [rules, setRules] = useState([]);
  const [type, setType] = useState("fact");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [avoidTerm, setAvoidTerm] = useState("");
  const [preferredTerm, setPreferredTerm] = useState("");

  const fetchRules = async () => {
    const res = await api.get("/api/brand-kit/");
    setRules(res.data.rules || []);
  };

  useEffect(() => { fetchRules(); }, []);

  const addRule = async () => {
    if (!title || !content) return alert("Fill in title and description");
    await api.post("/api/brand-kit/", {
      type, title, content,
      avoid_term: avoidTerm || null,
      preferred_term: preferredTerm || null,
    });
    setTitle(""); setContent(""); setAvoidTerm(""); setPreferredTerm("");
    fetchRules();
  };

  const deleteRule = async (id) => {
    await api.delete(`/api/brand-kit/${id}`);
    fetchRules();
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Brand Kit</h1>
      <p className="text-sm text-gray-500 mb-4">Define facts, tone rules, and terminology that Vouch will check content against.</p>

      <div className="border rounded-lg p-4 mb-6 space-y-3 bg-gray-50">
        <select value={type} onChange={(e) => setType(e.target.value)} className="border p-2 rounded w-full">
          <option value="fact">Fact</option>
          <option value="tone">Tone Rule</option>
          <option value="terminology">Terminology</option>
        </select>
        <input className="border p-2 rounded w-full" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <textarea className="border p-2 rounded w-full" placeholder="Rule description" value={content} onChange={(e) => setContent(e.target.value)} />
        {type === "terminology" && (
          <>
            <input className="border p-2 rounded w-full" placeholder="Avoid term (e.g. log in)" value={avoidTerm} onChange={(e) => setAvoidTerm(e.target.value)} />
            <input className="border p-2 rounded w-full" placeholder="Preferred term (e.g. sign in)" value={preferredTerm} onChange={(e) => setPreferredTerm(e.target.value)} />
          </>
        )}
        <button onClick={addRule} className="bg-black text-white px-4 py-2 rounded">Add Rule</button>
      </div>

      <div className="space-y-2">
        {rules.map((r) => (
          <div key={r.id} className="border rounded p-3 flex justify-between items-start bg-white">
            <div>
              <span className="text-xs font-semibold uppercase text-gray-500">{r.type}</span>
              <p className="font-medium">{r.title}</p>
              <p className="text-sm text-gray-600">{r.content}</p>
            </div>
            <button onClick={() => deleteRule(r.id)} className="text-red-600 text-sm">Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
}