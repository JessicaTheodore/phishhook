from collections import defaultdict
from .categories import CATEGORIES

class PlayerState:
    """Tracks a recency-weighted miss rate per category (the 'weak spots')."""
    def __init__(self, decay: float = 0.8):
        self.decay = decay
        self.miss = {c: 0.5 for c in CATEGORIES}       # prior: unknown
        self.attempts = defaultdict(int)
        self.correct = defaultdict(int)
        self.last_missed = None
        self.history = []          # [{category, correct}]
        self.streak = 0
        self.best_streak = 0

    def record(self, category: str, was_correct: bool):
        self.attempts[category] += 1
        self.correct[category] += was_correct
        self.miss[category] = self.decay * self.miss[category] + (1 - self.decay) * (0 if was_correct else 1)
        self.last_missed = None if was_correct else category
        self.history.append({'category': category, 'correct': bool(was_correct)})
        self.streak = self.streak + 1 if was_correct else 0
        self.best_streak = max(self.best_streak, self.streak)

    def weak_spots(self):
        return sorted(self.miss.items(), key=lambda kv: -kv[1])
