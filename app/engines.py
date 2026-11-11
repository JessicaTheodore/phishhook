"""Four ways to pick the next email. Each takes (state, bank) and returns an email dict."""
import random
from .categories import CATEGORIES

def _pick(bank, category, level=None):
    pool = [e for e in bank if e["category"] == category]
    if level:
        close = [e for e in pool if abs(e["difficulty"] - level) <= 1]
        pool = close or pool
    return random.choice(pool)

class RandomEngine:
    name = "random"
    def next(self, state, bank): return random.choice(bank)

class FixedEngine:
    """Fixed hard difficulty for everyone."""
    name = "fixed"
    def next(self, state, bank):
        return _pick(bank, random.choice(CATEGORIES), level=4)

class RulesEngine:
    """Edwin-style baseline: if the last answer was a miss, repeat that category; else random."""
    name = "rules"
    def next(self, state, bank):
        cat = state.last_missed or random.choice(CATEGORIES)
        return _pick(bank, cat, level=3)

class AdaptiveEngine:
    """Samples category in proportion to recent miss rate; difficulty tracks skill in that category."""
    name = "adaptive"
    def next(self, state, bank):
        weights = [state.miss[c] + 0.05 for c in CATEGORIES]
        cat = random.choices(CATEGORIES, weights)[0]
        level = max(1, min(5, round(1 + 4 * (1 - state.miss[cat]))))
        return _pick(bank, cat, level)

ENGINES = {e.name: e for e in (RandomEngine, FixedEngine, RulesEngine, AdaptiveEngine)}
