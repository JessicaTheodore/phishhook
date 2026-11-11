"""Email categories. 'safe' is tracked too so false positives show up as a weak spot."""
PHISH_CATEGORIES = ["fake_links", "urgent_tone", "spoofed_sender"]
CATEGORIES = PHISH_CATEGORIES + ["safe"]
