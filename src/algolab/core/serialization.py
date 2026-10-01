"""Validation helpers shared by every model's from_dict().

Each model turns itself into plain JSON data with to_dict() and back
with from_dict(). Anything read from a file is untrusted (it may be
hand-edited, truncated, or from another program), so from_dict() checks
everything with these helpers and raises ValueError with a message that
is safe to show in the UI. Because validation finishes before any
object is returned, a screen can apply the result knowing it cannot
fail halfway.
"""

from __future__ import annotations

import math


JSON_SCALARS = (int, float, str, bool, type(None))


def check_scalar(value: object, label: str) -> None:
    """Allow only what plain JSON can represent (no nested lists/dicts)."""

    if not isinstance(value, JSON_SCALARS):
        raise ValueError(f"{label} is not a number, text, or null.")

    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{label} is not a finite number.")


def check_int(value: object, label: str) -> int:
    """Require a whole number (bool is rejected: True is not a count)."""

    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{label} must be a whole number.")

    return value


def check_number(value: object, label: str) -> float:
    """Require a finite number (bool is rejected)."""

    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
    ):
        raise ValueError(f"{label} must be a finite number.")

    return value


def check_dict(data: object, owner: str) -> dict:
    if not isinstance(data, dict):
        raise ValueError(f"{owner} data must be an object.")

    return data


def checked_list(
    data: object,
    owner: str,
    limit: int,
    key: str = "items",
) -> list:
    """Return data[key] as a list, validating its type and length.

    Elements are NOT checked here; use check_scalar / check_int on them
    as appropriate for the structure.
    """

    if not isinstance(data, dict) or key not in data:
        raise ValueError(f"{owner} data must contain a '{key}' list.")

    items = data[key]

    if not isinstance(items, list):
        raise ValueError(f"{owner} '{key}' must be a list.")

    if len(items) > limit:
        raise ValueError(
            f"A {owner.lower()} can hold at most {limit} items when "
            f"loaded from a file (this one has {len(items)})."
        )

    return items


def checked_scalar_items(
    data: object,
    owner: str,
    limit: int,
    key: str = "items",
) -> list:
    """checked_list() plus every element must be a JSON scalar."""

    items = checked_list(data, owner, limit, key)

    for position, item in enumerate(items):
        check_scalar(item, f"Item {position}")

    return list(items)


def checked_int_items(
    data: object,
    owner: str,
    limit: int,
    key: str = "values",
) -> list[int]:
    """checked_list() plus every element must be a whole number."""

    items = checked_list(data, owner, limit, key)

    return [
        check_int(item, f"Value {position}")
        for position, item in enumerate(items)
    ]