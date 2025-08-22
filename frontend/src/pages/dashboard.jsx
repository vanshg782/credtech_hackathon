import React, { useEffect, useState } from "react";
import api from "../services/api";

export default function Dashboard() {
  const [rows, setRows] = useState([]);
  const [selected, setSelected] = useState(null);
  const [history, setHistory] = useState([]);

  const load = async () => {
    const r = await api.get("/scores");
    setRows(r.data);
  };

  const loadHistory = async (issuer_id) => {
    const r = await api.get(`/scores/${issuer_id}/history`);
    setHistory(r.data);
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    // Optional: attach websocket for push refresh
    const ws = new WebSocket("ws://localhost:8000/ws/latest");
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === "scores_changed") load();
    };
    return () => ws.close();
  }, []);

  return (
    <div style={{padding:16}}>
      <h2>Credit Intelligence Dashboard</h2>
      <table border="1" cellPadding="8">
        <thead>
          <tr><th>Issuer</th><th>Asset Class</th><th>Score</th><th>When</th><th>Explain</th></tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.score_id}>
              <td>{r.issuer}</td>
              <td>{r.asset_class}</td>
              <td>{r.score.toFixed(1)}</td>
              <td>{new Date(r.ts).toLocaleString()}</td>
              <td>
                <button onClick={async ()=>{
                  setSelected(r);
                  await loadHistory(r.issuer_id);
                }}>View</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selected && (
        <ExplainPanel selected={selected} history={history} />
      )}
    </div>
  );
}

function ExplainPanel({ selected, history }) {
  const [top, setTop] = React.useState([]);
  useEffect(() => {
    async function run() {
      const res = await fetch(`/api/v1/explain/${selected.score_id}`);
      const data = await res.json();
      setTop(data);
    }
    run();
  }, [selected]);

  return (
    <div style={{marginTop:24}}>
      <h3>{selected.issuer} — Latest score: {selected.score.toFixed(1)}</h3>
      <h4>Top Drivers (SHAP)</h4>
      <ul>
        {top.map((t,i)=>(
          <li key={i}>
            <b>{t.feature}</b>: {t.value.toFixed(2)} (impact {t.shap.toFixed(3)})
          </li>
        ))}
      </ul>

      <h4>Trend</h4>
      <ol>
        {history.map(h=>(
          <li key={h.id}>{new Date(h.ts).toLocaleString()} → {h.score.toFixed(1)}</li>
        ))}
      </ol>
    </div>
  );
}
