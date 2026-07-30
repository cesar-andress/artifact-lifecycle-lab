"""Derive final load-bearing labels from blinded annotator dimensions.

Authoritative rule: docs/RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md (commit e41902c).
Does not use traces, outcomes, or conditions.
"""

from __future__ import annotations

from typing import Any

RELEVANCE_VALUES = frozenset(
    {"irrelevant", "contextually_relevant", "directly_relevant", "ambiguous"}
)
NECESSITY_VALUES = frozenset(
    {"not_necessary", "helpful_but_substitutable", "materially_necessary", "ambiguous"}
)
FINAL_VALUES = frozenset({"load_bearing", "non_load_bearing", "ambiguous"})

# Combinations that follow the derivation but warrant human audit.
WARNING_COMBINATIONS: dict[tuple[str, str], str] = {
    ("irrelevant", "materially_necessary"): "irrelevant_but_materially_necessary",
    ("contextually_relevant", "materially_necessary"): "contextual_but_materially_necessary",
    ("directly_relevant", "not_necessary"): "directly_relevant_but_not_necessary",
}


def derive_final_classification(
    reference_relevance: str,
    material_necessity: str,
) -> dict[str, Any]:
    """Return final label plus optional consistency warning metadata.

    Authoritative rule (stricter than earlier design drafts)::

        if relevance == ambiguous -> ambiguous
        elif necessity == ambiguous -> ambiguous
        elif relevance == directly_relevant and necessity == materially_necessary
            -> load_bearing
        elif relevance in {irrelevant, contextually_relevant} -> non_load_bearing
        elif necessity in {not_necessary, helpful_but_substitutable} -> non_load_bearing
        else -> ambiguous

    Note: ``contextually_relevant + materially_necessary`` is **not** load-bearing;
    it falls through to ``non_load_bearing`` via the relevance branch, with a warning.
    """
    relevance = (reference_relevance or "").strip().lower()
    necessity = (material_necessity or "").strip().lower()

    if relevance not in RELEVANCE_VALUES or necessity not in NECESSITY_VALUES:
        return {
            "final_classification": "ambiguous",
            "consistency_warning": True,
            "warning_code": "unsupported_input_combination",
            "reference_relevance": relevance,
            "material_necessity": necessity,
        }

    warning_code = WARNING_COMBINATIONS.get((relevance, necessity))
    consistency_warning = warning_code is not None

    if relevance == "ambiguous" or necessity == "ambiguous":
        final = "ambiguous"
    elif relevance == "directly_relevant" and necessity == "materially_necessary":
        final = "load_bearing"
    elif relevance in {"irrelevant", "contextually_relevant"}:
        final = "non_load_bearing"
    elif necessity in {"not_necessary", "helpful_but_substitutable"}:
        final = "non_load_bearing"
    else:
        final = "ambiguous"
        consistency_warning = True
        warning_code = warning_code or "unsupported_input_combination"

    return {
        "final_classification": final,
        "consistency_warning": consistency_warning,
        "warning_code": warning_code or "",
        "reference_relevance": relevance,
        "material_necessity": necessity,
    }
