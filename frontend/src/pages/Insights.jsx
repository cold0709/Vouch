import { useState, useEffect } from "react";
import { api } from "../api";

export default function Insights() {
  const [data, setData] = useState({ topIssues: [], gaps: [] });

  useEffect(() => {
    api.get("/api/insights/").then((res) => setData(res.data));
  }, []);

  const maxCount = Math.max(...data.topIssues.map((i) => i.count), 1);

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Governance Insights</h1>

      <h2 className="font-semibold mb-2">Most Violated Rules</h2>
      <div className="space-y-2 mb-6">
        {data.topIssues.map((issue, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="text-sm w-40 truncate">{issue.name}</span>
            <div className="bg-orange-500 h-4 rounded" style={{ width: `${(issue.count / maxCount) * 200}px` }} />
            <span className="text-xs">{issue.count}</span>
          </div>
        ))}
        {data.topIssues.length === 0 && <p className="text-sm text-gray-500">No data yet. Run some checks first.</p>}
      </div>

      <h2 className="font-semibold mb-2">Guideline Gaps Reported</h2>
      {data.gaps.length === 0 && <p className="text-sm text-gray-500">No gaps marked yet.</p>}
      {data.gaps.map((g, i) => (
        <div key={i} className="border rounded p-2 mb-2 text-sm">{g.explanation}</div>
      ))}
    </div>
  );
}