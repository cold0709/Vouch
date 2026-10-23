import { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";

const statusColors = {
  CONFLICT: "border-red-400 bg-red-50",
  UNVERIFIED: "border-yellow-400 bg-yellow-50",
};

const severityBadge = {
  high: "bg-red-600 text-white",
  medium: "bg-orange-500 text-white",
  low: "bg-gray-400 text-white",
};

function FindingCard({ finding, onAccept, onMarkGap }) {
  return (
    <div className={`border rounded-lg p-4 mb-3 ${statusColors[finding.status] || "border-gray-300"}`}>
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-bold uppercase">{finding.type.replace("_", " ")}</span>
        <span className={`text-xs px-2 py-1 rounded ${severityBadge[finding.severity]}`}>{finding.severity}</span>
      </div>

      {finding.status === "UNVERIFIED" ? (
        <p className="text-sm font-medium text-yellow-800 mb-1">⚠️ Unverified — No approved source found.</p>
      ) : (
        <p className="text-sm font-medium text-red-800 mb-1">🚫 Conflicts with Brand Kit</p>
      )}

      <p className="text-sm mb-2">{finding.explanation}</p>
      <p className="text-sm bg-white border rounded p-2 mb-2">
        <span className="line-through text-gray-500">{finding.original_snippet}</span>
        {finding.suggested_fix && <span className="text-green-700 font-medium"> → {finding.suggested_fix}</span>}
      </p>

      <div className="flex gap-2">
        {finding.suggested_fix && (
          <button onClick={() => onAccept(finding)} className="bg-black text-white text-sm px-3 py-1 rounded">
            Accept Suggestion
          </button>
        )}
        {finding.status === "UNVERIFIED" && (
          <button onClick={() => onMarkGap(finding)} className="border text-sm px-3 py-1 rounded">
            Mark as Guideline Gap
          </button>
        )}
      </div>
    </div>
  );
}

export default function ContentReview() {
  const { id } = useParams();
  const [content, setContent] = useState(null);
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [comment, setComment] = useState("");

  const loadContent = useCallback(async () => {
    const res = await api.get(`/api/content/${id}`);
    setContent(res.data.content);
    setFindings(res.data.findings || []);
  }, [id]);

  useEffect(() => { loadContent(); }, [loadContent]);

  const runCheck = async () => {
    setLoading(true);
    const res = await api.post("/api/check/", { content_id: id, text: content.current_text });
    setFindings(res.data.findings);
    setLoading(false);
  };

  const acceptSuggestion = async (finding) => {
    const updated = content.current_text.replace(finding.original_snippet, finding.suggested_fix);
    setContent({ ...content, current_text: updated });
    await api.put(`/api/content/${id}`, { title: content.title, text: updated });
  };

  const markGap = async (finding) => {
    await api.post(`/api/insights/mark-gap/${finding.id}`);
    alert("Marked as a guideline gap for the brand team to review.");
  };

  const submitForReview = async () => {
    await api.post("/api/review/", { content_id: id, decision: "PENDING_REVIEW", user_name: "Creator" });
    loadContent();
  };

  const approve = async () => {
    await api.post("/api/review/", { content_id: id, decision: "APPROVED", comment, user_name: "Reviewer" });
    loadContent();
  };

  if (!content) return <p className="p-6">Loading...</p>;

  return (
    <div className="max-w-5xl mx-auto p-6 grid grid-cols-2 gap-6">
      <div>
        <h1 className="text-xl font-bold mb-2">{content.title}</h1>
        <span className="text-xs bg-gray-200 px-2 py-1 rounded">{content.status}</span>
        <textarea
          className="w-full border rounded p-3 mt-3 h-64"
          value={content.current_text}
          onChange={(e) => setContent({ ...content, current_text: e.target.value })}
        />
        <div className="flex gap-2 mt-3">
          <button onClick={runCheck} disabled={loading} className="bg-black text-white px-4 py-2 rounded">
            {loading ? "Checking..." : "Run Brand Check"}
          </button>
          <button onClick={submitForReview} className="border px-4 py-2 rounded">Submit for Review</button>
        </div>

        <div className="mt-6 border-t pt-4">
          <p className="text-xs text-gray-500">
            🔒 Content processed via Groq (Llama 3.3) for AI-assisted review. No auto-publish — human approval required.
          </p>
        </div>
      </div>

      <div>
        <h2 className="font-semibold mb-2">Findings ({findings.length})</h2>
        {findings.length === 0 && <p className="text-sm text-gray-500">No issues found yet. Run a check.</p>}
        {findings.map((f, i) => (
          <FindingCard key={i} finding={f} onAccept={acceptSuggestion} onMarkGap={markGap} />
        ))}

        <div className="mt-6 border-t pt-4">
          <h3 className="font-semibold mb-2">Reviewer Action</h3>
          <textarea
            placeholder="Add a comment..."
            className="w-full border rounded p-2 mb-2"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
          <button onClick={approve} className="bg-black text-white px-4 py-2 rounded">Approve Content</button>
        </div>
      </div>
    </div>
  );
}