"""Semantic checks that JSON Schema cannot express by itself."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class ContractSemanticError(ValueError):
    """A structurally valid contract payload violates a cross-field rule."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


def validate_search_request_semantics(request: Mapping[str, Any]) -> None:
    """Reject duplicate active feature IDs after structural schema validation.

    ``uniqueItems`` cannot detect two criteria with the same ``feature_id`` and
    different weights. The API should run JSON Schema validation first, then
    this check, then validate compatibility against the selected catalog.
    """
    criteria = request.get("criteria")
    if not isinstance(criteria, Sequence) or isinstance(criteria, (str, bytes)):
        return

    seen: set[str] = set()
    duplicates: list[str] = []
    for criterion in criteria:
        if not isinstance(criterion, Mapping):
            continue
        feature_id = criterion.get("feature_id")
        if not isinstance(feature_id, str):
            continue
        if feature_id in seen and feature_id not in duplicates:
            duplicates.append(feature_id)
        seen.add(feature_id)

    if duplicates:
        raise ContractSemanticError(
            "DUPLICATE_FEATURE_ID",
            "Each active feature_id must occur exactly once in criteria.",
            details={"feature_ids": duplicates},
        )


def validate_dataset_manifest_semantics(manifest: Mapping[str, Any]) -> None:
    """Require a recorded reason for each null metadata value in a manifest.

    Call after JSON Schema validation. Reason fields themselves and a null
    ``synthetic_reason`` on real manifests are not missing source metadata.
    """
    reasons = manifest.get("missing_reasons", {})
    if not isinstance(reasons, Mapping):
        return

    unexplained: list[str] = []
    reason_fields = {
        "missing_reason",
        "geometry_missing_reason",
        "vertical_reference_missing_reason",
        "resolution_missing_reason",
        "synthetic_reason",
    }

    def visit(value: Any, path: str = "") -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                child_path = f"{path}.{key}" if path else str(key)
                if child is None:
                    if key not in reason_fields and child_path not in reasons:
                        unexplained.append(child_path)
                else:
                    visit(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                child_path = f"{path}[{index}]"
                if child is None:
                    if child_path not in reasons:
                        unexplained.append(child_path)
                else:
                    visit(child, child_path)

    visit(manifest)
    if unexplained:
        raise ContractSemanticError(
            "MISSING_REASON_REQUIRED",
            "Every null manifest value must have a field-specific missing reason.",
            details={"paths": unexplained},
        )
