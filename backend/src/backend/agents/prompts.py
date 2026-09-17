from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parents[1] / "ai" / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / f"{name}.txt").read_text(encoding="utf-8")
