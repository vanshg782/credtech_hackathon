import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [message, setMessage] = useState("Loading backend...");
  const [scores, setScores] = useState([]);

  useEffect(() => {
    const fetchBackend = async () => {
      try {
        // 1️⃣ Check backend health
        const healthRes = await axios.get("/health");
        setMessage(healthRes.data.message || "Backend connected ✅");

        // 2️⃣ Fetch latest scores
        const scoresRes = await axios.get("/api/v1/scores");
        setScores(scoresRes.data);
      } catch (err) {
        console.error("Error connecting to backend:", err);
        setMessage("❌ Could not connect to backend");
      }
    };

    fetchBackend();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>CredTech Hackathon 🚀</h1>
        <p>{message}</p>

        {scores.length === 0 ? (
          <p>Loading scores...</p>
        ) : (
          <table border="1" cellPadding="10">
            <thead>
              <tr>
                <th>Issuer</th>
                <th>Asset Class</th>
                <th>Score</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {scores.map((s) => (
                <tr key={s.score_id}>
                  <td>{s.issuer}</td>
                  <td>{s.asset_class}</td>
                  <td>{s.score}</td>
                  <td>{new Date(s.ts).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </header>
    </div>
  );
}

export default App;
