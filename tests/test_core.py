import random
from app.generator import build_bank
from app.engines import ENGINES
from app.player import PlayerState
from app.phishscale import difficulty

def test_bank_and_engines():
    bank = build_bank(per_cell=2, use_llm=False)
    for name, E in ENGINES.items():
        assert E().next(PlayerState(), bank)["id"], name

def test_fewer_cues_is_harder():
    assert difficulty(0, 4) > difficulty(4, 4)

def test_adaptive_targets_weak_category():
    random.seed(1)
    bank = build_bank(per_cell=3, use_llm=False); s = PlayerState()
    for _ in range(15): s.record("fake_links", False); s.record("urgent_tone", True)
    picks = [ENGINES["adaptive"]().next(s, bank)["category"] for _ in range(200)]
    assert picks.count("fake_links") > picks.count("urgent_tone")
