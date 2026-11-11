"""Simplified NIST Phish Scale (Steves et al., 2020).

Official scale: count red-flag cues, rate premise alignment (how well the story fits
the reader), combine into easy/moderate/hard. This is a 1-5 SIMPLIFICATION.
TODO: replace with the official cue list + premise alignment rubric from the NIST paper.
Higher difficulty = harder to spot (fewer cues, better premise alignment).
"""

def cue_component(n_cues: int) -> int:
    return {0: 5, 1: 4, 2: 3, 3: 2}.get(n_cues, 1)

def difficulty(n_cues: int, premise_alignment: int) -> int:
    """premise_alignment: 1 (generic) .. 5 (very tailored to the reader)."""
    return max(1, min(5, round((cue_component(n_cues) + premise_alignment) / 2)))
