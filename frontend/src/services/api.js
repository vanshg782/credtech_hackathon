import React, { useEffect, useState } from "react";
import { getScores } from "./services/api"; // import your updated api.js
import "./App.css";

function App() {
  const [message, setMessage] = useState("Connecting to backend...");
  const [scores, setScores] = useState([]);

  // Fetch latest scores from backend
  const fetchScores = async () => {
    try {
      const res = await getScores();
      setScores(res.data);
      setMessage("Backend connected ✅");
    } catch (err) {
      console.error("Error connecting to backend:", err);
      setMessage("❌ Could not connect to backend, retrying...");
      // Retry after 5 seconds
      setTimeout(fetchScores, 5000);
    }
  };

  useEffect(() => {
    fetchScores();
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
