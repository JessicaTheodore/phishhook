"""Simulated players. ASSUMPTION (document in report): skill grows when a category is practiced
with feedback, and faster on misses. Tune lr/penalty from published findings."""
import csv, json, random, statistics
from .categories import CATEGORIES
from .engines import ENGINES
from .player import PlayerState

def make_player():
    skill = {c: random.uniform(0.65, 0.9) for c in CATEGORIES}
    skill[random.choice(CATEGORIES)] = random.uniform(0.3, 0.5)   # one weak spot
    return skill

def run(engine_name, bank, n_players=100, rounds=60, lr=0.08, penalty=0.1):
    rows = []
    for pid in range(n_players):
        skill, state, eng = make_player(), PlayerState(), ENGINES[engine_name]()
        for r in range(1, rounds + 1):
            e = eng.next(state, bank)
            p = max(0.05, min(0.98, skill[e["category"]] - penalty * (e["difficulty"] - 3)))
            ok = random.random() < p
            state.record(e["category"], ok)
            skill[e["category"]] += lr * (1 - skill[e["category"]]) * (0.5 if ok else 1.0)
            rows.append((engine_name, pid, r, min(skill.values())))
    return rows

if __name__ == "__main__":
    random.seed(42)
    bank = json.load(open("data/email_bank.json"))
    allrows = [r for n in ENGINES for r in run(n, bank)]
    with open("results/simulation.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["engine", "player", "round", "weakest_skill"]); w.writerows(allrows)
    for n in ENGINES:
        final = [r[3] for r in allrows if r[0] == n and r[2] == 60]
        print(f"{n:9s} weakest-category skill after 60 rounds: {statistics.mean(final):.3f}")
