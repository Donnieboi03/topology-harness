"""Evidence gates for Critiquer / refine-loop exits."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

# Hard exits for code/doc refine-loop work (fail → another producer round).
CODE_GATES: tuple[str, ...] = (
    "tests",
    "typecheck",
    "lint_syntax",
    "docs",
)

# Per-atom analogous evidence when the topic is not primarily code.
ATOM_GATES: dict[str, tuple[str, ...]] = {
    "research-swarm": ("citations", "disjoint_coverage", "no_raw_vault_dump"),
    "refine-loop": CODE_GATES,
    "debate": ("tie_break_recorded", "consul_decision", "expand_vs_cut_args"),
    "plane-audit": ("all_planes_clear", "non_overlapping_lenses"),
    "verify-claims": ("claims_extracted", "blinded_verification", "reconciled_facts"),
}


def gates_for(atom_or_domain: str = "code") -> tuple[str, ...]:
    """Return gate names for an atom verb or the ``code`` domain."""
    key = (atom_or_domain or "code").strip().lower()
    if key in {"code", "docs", "refine", "refine-loop"}:
        return CODE_GATES
    return ATOM_GATES.get(key, CODE_GATES)


def checklist(atom_or_domain: str = "code") -> list[dict[str, Any]]:
    """Structured unchecked checklist suitable for Critiquer briefs."""
    return [{"gate": g, "passed": False, "evidence": ""} for g in gates_for(atom_or_domain)]


def all_gates_passed(results: Mapping[str, Any] | Iterable[Mapping[str, Any]]) -> bool:
    """True when every required gate has a truthy pass signal.

    Accepts either ``{gate_name: bool|dict}`` or a list of
    ``{"gate": name, "passed": bool}`` rows.
    """
    if isinstance(results, Mapping):
        # Mapping form: missing keys count as fail for CODE_GATES-style sets
        # when callers pass a full gate→status map; for partial maps, require
        # every provided value to be passed AND at least one gate present.
        if not results:
            return False
        for key, val in results.items():
            if isinstance(val, Mapping):
                if not bool(val.get("passed")):
                    return False
            elif not bool(val):
                return False
        return True

    rows = list(results)
    if not rows:
        return False
    for row in rows:
        if not bool(row.get("passed")):
            return False
    return True


def missing_gates(
    results: Mapping[str, Any],
    *,
    required: Iterable[str] | None = None,
) -> list[str]:
    """Names of required gates that are missing or not passed."""
    need = list(required) if required is not None else list(CODE_GATES)
    missing: list[str] = []
    for gate in need:
        val = results.get(gate)
        if val is None:
            missing.append(gate)
            continue
        if isinstance(val, Mapping):
            if not bool(val.get("passed")):
                missing.append(gate)
        elif not bool(val):
            missing.append(gate)
    return missing
