import json, os, uuid
from flask import Flask, jsonify, render_template, request
from .engines import ENGINES
from .generator import build_bank
from .player import PlayerState

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0   # always serve fresh CSS while developing
BANK_PATH = "data/email_bank.json"
BANK = json.load(open(BANK_PATH)) if os.path.exists(BANK_PATH) else build_bank(use_llm=False)
PLAYERS = {}   # in-memory prototype; no real user data stored

@app.get("/")
def game(): return render_template("game.html", page="game")

@app.get("/dashboard")
def dashboard(): return render_template("dashboard.html", page="dash")

@app.post("/api/start")
def start():
    pid = uuid.uuid4().hex[:8]
    mode = request.json.get("mode", "adaptive")
    PLAYERS[pid] = (PlayerState(), ENGINES[mode]())
    return jsonify(player=pid, mode=mode)

@app.get("/api/next/<pid>")
def nxt(pid):
    state, eng = PLAYERS[pid]
    e = eng.next(state, BANK)
    return jsonify({k: e[k] for k in ("id", "from", "subject", "body")})   # no answer leaked

@app.post("/api/answer/<pid>")
def answer(pid):
    state, _ = PLAYERS[pid]
    e = next(x for x in BANK if x["id"] == request.json["id"])
    ok = request.json["says_phish"] == e["is_phish"]
    state.record(e["category"], ok)
    return jsonify(correct=ok, category=e["category"], cues=e["cues"], difficulty=e["difficulty"])

@app.get("/api/stats/<pid>")
def stats(pid):
    if pid not in PLAYERS:
        return jsonify(error="unknown player"), 404
    s, eng = PLAYERS[pid]
    cats = {c: {"attempts": s.attempts[c], "correct": s.correct[c], "miss": round(m, 3)} for c, m in s.miss.items()}
    rounds = len(s.history)
    right = sum(h["correct"] for h in s.history)
    return jsonify(mode=eng.name, rounds=rounds, correct=right,
                   accuracy=round(right / rounds, 3) if rounds else None,
                   streak=s.streak, best_streak=s.best_streak, categories=cats,
                   focus=s.weak_spots()[0][0] if rounds else None, recent=s.history[-12:])

if __name__ == "__main__":
    app.run(debug=True)
