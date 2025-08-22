from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from db import Base, engine, get_db
from models import Issuer, CreditScore, FeatureAttribution
from scheduler import start_scheduler
from sqlalchemy import func
import asyncio

app = FastAPI(title="Credit Intelligence Platform", version="0.1.0")

# ---------------------------
# Middleware
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.1.6:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# DB Init + Scheduler
# ---------------------------
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    start_scheduler()

# ---------------------------
# API Routes
# ---------------------------
@app.get("/")
def root():
    return {
        "message": "✅ Credit Intelligence Backend is running successfully!",
        "docs": "/docs",
        "features": [
            "📊 Issuer-level and asset-class-level scores",
            "⚡ Real-time SHAP explanations",
            "📈 Historical score trends",
            "🔔 WebSocket live updates"
        ],
        "endpoints": [
            "/api/v1/issuers",
            "/api/v1/issuers/{id}",
            "/api/v1/scores",
            "/api/v1/scores/{issuer_id}/history",
            "/api/v1/explain/{score_id}",
            "/api/v1/refresh",
            "/health",
            "/ws/latest"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is healthy 🚀"}

@app.get("/api/v1/issuers")
def list_issuers(db: Session = Depends(get_db)):
    rows = db.query(Issuer).all()
    return [{"id": r.id, "name": r.name, "asset_class": r.asset_class} for r in rows]

@app.get("/api/v1/issuers/{issuer_id}")
def get_issuer(issuer_id: int, db: Session = Depends(get_db)):
    issuer = db.query(Issuer).filter(Issuer.id == issuer_id).first()
    if not issuer:
        return {"error": "Issuer not found"}
    return {"id": issuer.id, "name": issuer.name, "asset_class": issuer.asset_class}

@app.get("/api/v1/scores")
def latest_scores(asset_class: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(CreditScore).join(Issuer)
    if asset_class:
        q = q.filter(Issuer.asset_class == asset_class)

    out = {}
    for s in q.order_by(CreditScore.ts.desc()).all():
        if s.issuer.name in out:
            continue
        out[s.issuer.name] = {
            "issuer": s.issuer.name,
            "asset_class": s.issuer.asset_class,
            "score": s.score,
            "ts": s.ts,
            "model_version": s.model_version,
            "issuer_id": s.issuer_id,
            "score_id": s.id,
        }
    return list(out.values())

@app.get("/api/v1/scores/{issuer_id}/history")
def score_history(issuer_id: int, db: Session = Depends(get_db)):
    q = db.query(CreditScore).filter(CreditScore.issuer_id == issuer_id).order_by(CreditScore.ts.asc()).all()
    return [{"ts": s.ts, "score": s.score, "id": s.id} for s in q]

@app.get("/api/v1/explain/{score_id}")
def explain(score_id: int, db: Session = Depends(get_db)):
    rows = db.query(FeatureAttribution).filter(FeatureAttribution.score_id == score_id).all()
    rows = sorted(rows, key=lambda r: abs(r.shap_value), reverse=True)
    top = rows[:8]
    return [{"feature": r.feature_name, "value": r.feature_value, "shap": r.shap_value} for r in top]

@app.post("/api/v1/refresh")
def refresh_scores():
    """
    Manually trigger refresh (could be linked to scheduler or ML pipeline).
    """
    # TODO: hook your ingestion + model scoring pipeline here
    return {"status": "ok", "message": "Data refresh triggered 🔄"}

# ---------------------------
# WebSocket for live updates
# ---------------------------
@app.websocket("/ws/latest")
async def ws_latest(websocket: WebSocket):
    await websocket.accept()
    last_count = -1
    try:
        while True:
            await asyncio.sleep(5)
            with get_db() as db:
                count = db.query(func.count(CreditScore.id)).scalar()
            if count != last_count:
                await websocket.send_json({"type": "scores_changed", "count": int(count)})
                last_count = count
    except WebSocketDisconnect:
        print("🔌 WebSocket client disconnected")
