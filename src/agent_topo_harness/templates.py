"""Load markdown templates from agent-topo-harness/docs."""
from __future__ import annotations

from pathlib import Path

# agent-topo-harness/docs (package at …/src/agent_topo_harness → parents[2] = harness root)
_DEFAULT_DOCS = Path(__file__).resolve().parents[2] / "docs"


def skill_refs_dir() -> Path:
    """Alias for :func:`docs_dir`."""
    return docs_dir()


def docs_dir() -> Path:
    return _DEFAULT_DOCS


def load_template(name: str, *, refs_dir: Path | None = None) -> str:
    """Load a markdown file from the harness docs directory.

    ``name`` may be a bare stem (``compounds``), a filename (``compounds.md``),
    or a relative path under docs/.
    """
    base = refs_dir or docs_dir()
    raw = (name or "").strip()
    if not raw:
        raise ValueError("template name is required")

    candidates = [
        base / raw,
        base / f"{raw}.md" if not raw.endswith(".md") else base / raw,
    ]
    for path in candidates:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"template not found under {base}: {name!r}")


def list_templates(*, refs_dir: Path | None = None) -> list[str]:
    base = refs_dir or skill_refs_dir()
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.glob("*.md"))
