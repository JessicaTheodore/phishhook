"""Practice-email generation. LLM if ANTHROPIC_API_KEY is set, else offline templates.
All brands are fictional and all links are non-working (.invalid domains)."""
import json, os, random, uuid
from .categories import PHISH_CATEGORIES
from .phishscale import difficulty

BRANDS = ["Northwind Bank", "Contoso Cloud", "Fabrikam Payroll", "Tailspin Shipping"]

# cue pool per category; easy emails include more of them
CUES = {
    "fake_links": ["link text says one domain but points to another", "misspelled domain", "raw IP/odd URL", "login link on unrelated domain"],
    "urgent_tone": ["threatens account closure", "short deadline", "ALL CAPS warning", "pressure to act now"],
    "spoofed_sender": ["display name does not match address", "lookalike domain", "generic greeting", "free-mail address for a company"],
}
BODY = {
    "fake_links": "Your {brand} statement is ready. View it here: http://{brand_slug}-secure.example.invalid/login",
    "urgent_tone": "Your {brand} account will be CLOSED in 24 hours unless you confirm your details immediately.",
    "spoofed_sender": "Hello, this is {brand} support. Please review the policy update and reply with your employee ID.",
}
SAFE = [
    ("Team lunch Friday", "Hi all, we're getting lunch at noon Friday. Reply if you have dietary needs. - Dana"),
    ("Q4 planning notes", "Notes from today's planning meeting are in the shared drive. Let me know if I missed anything."),
    ("Password policy reminder", "As announced last month, passwords rotate quarterly. Use the portal you normally use; no action needed via email."),
]

def offline_email(category: str, level: int | None = None) -> dict:
    brand = random.choice(BRANDS)
    if category == "safe":
        subj, body = random.choice(SAFE)
        return {"id": uuid.uuid4().hex[:8], "category": "safe", "is_phish": False, "brand": "n/a",
                "from": "colleague@company.example", "subject": subj, "body": body,
                "cues": [], "premise_alignment": random.randint(2, 5), "difficulty": random.randint(1, 5)}
    level = level or random.randint(1, 5)
    n_cues = max(0, 5 - level)                      # harder = fewer cues
    cues = random.sample(CUES[category], min(n_cues, len(CUES[category])))
    pa = min(5, max(1, level + random.choice([-1, 0, 1])))
    slug = brand.lower().replace(" ", "-")
    return {"id": uuid.uuid4().hex[:8], "category": category, "is_phish": True, "brand": brand,
            "from": f"support@{slug}.example.invalid", "subject": f"Action needed: {brand}",
            "body": BODY[category].format(brand=brand, brand_slug=slug),
            "cues": cues, "premise_alignment": pa, "difficulty": difficulty(len(cues), pa)}

def llm_email(category: str, level: int) -> dict:
    import anthropic
    client = anthropic.Anthropic()
    prompt = (f"Write ONE fictional practice email for a phishing-awareness game. Category: {category}. "
              f"Target difficulty {level}/5 (5 = very convincing, few red flags). Use a fictional brand, no real "
              "links (use .invalid domains). Return ONLY JSON with keys: subject, from, body, cues (list of "
              "red-flag cues actually present), premise_alignment (int 1-5), brand.")
    r = client.messages.create(model=os.getenv("LLM_MODEL", "claude-sonnet-5-5"), max_tokens=1000,
                               messages=[{"role": "user", "content": prompt}])
    d = json.loads(r.content[0].text.replace("```json", "").replace("```", "").strip())
    d.update(id=uuid.uuid4().hex[:8], category=category, is_phish=True,
             difficulty=difficulty(len(d["cues"]), int(d["premise_alignment"])), needs_review=True)
    return d  # needs_review: spot-check by hand before it enters the bank

def build_bank(per_cell: int = 3, use_llm: bool | None = None) -> list[dict]:
    use_llm = bool(os.getenv("ANTHROPIC_API_KEY")) if use_llm is None else use_llm
    bank = []
    for cat in PHISH_CATEGORIES:
        for lvl in range(1, 6):
            for _ in range(per_cell):
                bank.append(llm_email(cat, lvl) if use_llm else offline_email(cat, lvl))
    bank += [offline_email("safe") for _ in range(per_cell * 5)]
    return bank

if __name__ == "__main__":
    bank = build_bank()
    json.dump(bank, open("data/email_bank.json", "w"), indent=2)
    print(f"Wrote {len(bank)} emails to data/email_bank.json")
