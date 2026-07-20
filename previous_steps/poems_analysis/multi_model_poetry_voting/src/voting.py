from __future__ import annotations

from collections import Counter

from src.schemas import ModelResult, VoteDecision


def choose_vote(results_by_provider: dict[str, ModelResult]) -> VoteDecision:
    usable = {
        provider: result
        for provider, result in results_by_provider.items()
        if result.status == "ok"
    }
    if not usable:
        return VoteDecision(
            voted_label="no",
            selected_provider="",
            selected_model_name="",
            selected_confidence=0.0,
            final_span="",
            vote_reason="no_successful_model_outputs",
        )

    counts = Counter(result.label for result in usable.values())
    top_label, top_count = counts.most_common(1)[0]

    if top_count >= 2:
        voted_label = top_label
        vote_reason = "majority_vote"
    else:
        highest = max(usable.values(), key=lambda item: item.confidence)
        voted_label = highest.label
        vote_reason = "highest_confidence_tiebreak"

    supporting = [result for result in usable.values() if result.label == voted_label]
    winner = max(supporting, key=lambda item: item.confidence)

    return VoteDecision(
        voted_label=voted_label,
        selected_provider=winner.provider,
        selected_model_name=winner.model_name,
        selected_confidence=winner.confidence,
        final_span=winner.span,
        vote_reason=vote_reason,
    )
