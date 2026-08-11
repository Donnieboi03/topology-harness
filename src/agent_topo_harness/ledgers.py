"""Magentic-style Task / Progress ledgers + stall policy (portable schemas).

Hosts persist these on TO ``StickyHandle.meta`` (see sticky helpers). Do not
wipe sticky TT sessions on replan — revise the Task Ledger / TO brief only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


@dataclass
class ReasonedBool:
    """Progress-ledger cell: boolean plus short rationale."""

    answer: bool
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"answer": bool(self.answer), "reason": str(self.reason or "")}

    @classmethod
    def from_dict(cls, raw: Any) -> ReasonedBool:
        if isinstance(raw, ReasonedBool):
            return raw
        if isinstance(raw, Mapping):
            return cls(
                answer=bool(raw.get("answer")),
                reason=str(raw.get("reason") or ""),
            )
        return cls(answer=bool(raw), reason="")


@dataclass
class TaskLedger:
    """Outer-loop facts survey + plan hint (TO-owned)."""

    given_or_verified: list[str] = field(default_factory=list)
    facts_to_lookup: list[dict[str, str]] = field(default_factory=list)
    facts_to_derive: list[str] = field(default_factory=list)
    educated_guesses: list[dict[str, str]] = field(default_factory=list)
    plan_bullets: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "given_or_verified": list(self.given_or_verified),
            "facts_to_lookup": [dict(x) for x in self.facts_to_lookup],
            "facts_to_derive": list(self.facts_to_derive),
            "educated_guesses": [dict(x) for x in self.educated_guesses],
            "plan_bullets": [dict(x) for x in self.plan_bullets],
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | None) -> TaskLedger:
        if not raw:
            return cls()
        lookup = []
        for item in raw.get("facts_to_lookup") or []:
            if isinstance(item, Mapping):
                lookup.append(
                    {
                        "fact": str(item.get("fact") or ""),
                        "where": str(item.get("where") or ""),
                    }
                )
            else:
                lookup.append({"fact": str(item), "where": ""})
        guesses = []
        for item in raw.get("educated_guesses") or []:
            if isinstance(item, Mapping):
                guesses.append(
                    {
                        "guess": str(item.get("guess") or ""),
                        "reason": str(item.get("reason") or ""),
                    }
                )
            else:
                guesses.append({"guess": str(item), "reason": ""})
        plan = []
        for item in raw.get("plan_bullets") or []:
            if isinstance(item, Mapping):
                plan.append(
                    {
                        "step": str(item.get("step") or ""),
                        "owner_lane": str(item.get("owner_lane") or ""),
                    }
                )
            else:
                plan.append({"step": str(item), "owner_lane": ""})
        return cls(
            given_or_verified=[str(x) for x in (raw.get("given_or_verified") or [])],
            facts_to_lookup=lookup,
            facts_to_derive=[str(x) for x in (raw.get("facts_to_derive") or [])],
            educated_guesses=guesses,
            plan_bullets=plan,
        )

    def summary_line(self) -> str:
        n_v = len(self.given_or_verified)
        n_l = len(self.facts_to_lookup)
        n_p = len(self.plan_bullets)
        return f"task_ledger verified={n_v} lookup={n_l} plan={n_p}"


@dataclass
class ProgressLedger:
    """Inner-round control artifact (TO-owned between TT turns)."""

    is_request_satisfied: ReasonedBool = field(
        default_factory=lambda: ReasonedBool(False, "")
    )
    is_in_loop: ReasonedBool = field(default_factory=lambda: ReasonedBool(False, ""))
    is_progress_being_made: ReasonedBool = field(
        default_factory=lambda: ReasonedBool(True, "")
    )
    next_speaker: str = ""
    instruction_or_question: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_request_satisfied": self.is_request_satisfied.to_dict(),
            "is_in_loop": self.is_in_loop.to_dict(),
            "is_progress_being_made": self.is_progress_being_made.to_dict(),
            "next_speaker": str(self.next_speaker or ""),
            "instruction_or_question": str(self.instruction_or_question or ""),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | None) -> ProgressLedger:
        if not raw:
            return cls()
        return cls(
            is_request_satisfied=ReasonedBool.from_dict(
                raw.get("is_request_satisfied")
            ),
            is_in_loop=ReasonedBool.from_dict(raw.get("is_in_loop")),
            is_progress_being_made=ReasonedBool.from_dict(
                raw.get("is_progress_being_made")
            ),
            next_speaker=str(raw.get("next_speaker") or ""),
            instruction_or_question=str(raw.get("instruction_or_question") or ""),
        )

    def summary_line(self) -> str:
        return (
            f"progress satisfied={self.is_request_satisfied.answer} "
            f"loop={self.is_in_loop.answer} progressing={self.is_progress_being_made.answer} "
            f"next={self.next_speaker or '-'}"
        )


@dataclass
class StallState:
    """Counters persisted on TO meta under ``stall``."""

    stall_count: int = 0
    reset_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "stall_count": int(self.stall_count),
            "reset_count": int(self.reset_count),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | None) -> StallState:
        if not raw:
            return cls()
        return cls(
            stall_count=int(raw.get("stall_count") or 0),
            reset_count=int(raw.get("reset_count") or 0),
        )


@dataclass
class StallPolicy:
    """Stall → replan without wiping sticky TT sessions."""

    max_stall: int = 3
    max_reset: int = 2

    def note_round(
        self,
        state: StallState,
        ledger: ProgressLedger,
        *,
        evidence_fail_streak: bool = False,
    ) -> StallState:
        """Update stall counters from a progress ledger (+ optional evidence FAIL)."""
        stalled = (
            (not ledger.is_progress_being_made.answer)
            or ledger.is_in_loop.answer
            or evidence_fail_streak
        )
        if stalled:
            state.stall_count = int(state.stall_count) + 1
        else:
            state.stall_count = max(0, int(state.stall_count) - 1)
        return state

    def should_replan(self, state: StallState) -> bool:
        return int(state.stall_count) > int(self.max_stall)

    def mark_replan(self, state: StallState) -> StallState:
        """After a brief revise / replan: bump reset, clear stall streak."""
        state.reset_count = int(state.reset_count) + 1
        state.stall_count = 0
        return state

    def should_escalate(self, state: StallState) -> bool:
        return int(state.reset_count) >= int(self.max_reset)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
