"""
color_registry.py
Session-level Category-to-Color Registry (`02_color_registry.json`).

Ensures that the same data entity (e.g., "台北") receives the exact same color slot
across every Format D chart and Format E dashboard in a reading session, regardless of
sort order, subset filtering, or script invocation boundaries.

Note: `hcl_color_engine` is the public entry point; this module may also be imported directly.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import color_core as _hce

REGISTRY_FILENAME = "02_color_registry.json"

_ACTIVE_REGISTRY: Optional["CategoryColorRegistry"] = None
_ASCII_LETTER_RE = re.compile(r"[A-Za-z]+")


class RegistryFullError(ValueError):
    """Raised when registering a new category would exceed `max_slots` and overflow='raise'."""


def _raw_normalize(name: object) -> str:
    """Normalize NFKC + strip and casefold ASCII Latin letters (matching JS normalizeEntityKey)."""
    s = unicodedata.normalize("NFKC", str(name)).strip()
    return _ASCII_LETTER_RE.sub(lambda m: m.group(0).lower(), s)


def _is_na_marker(raw: object) -> bool:
    if raw is None:
        return True
    s = str(raw).strip()
    if not s:
        return True
    s_nfkc = unicodedata.normalize("NFKC", s).strip()
    return (
        s.lower() in _hce.KNOWN_NA_STRINGS
        or s in _hce.KNOWN_NA_STRINGS
        or s_nfkc.lower() in _hce.KNOWN_NA_STRINGS
    )


def _is_reserved_other(raw: object) -> bool:
    if raw is None:
        return False
    s = str(raw).strip()
    s_nfkc = unicodedata.normalize("NFKC", s).strip()
    return (
        s in _hce.RESERVED_OTHER_LABELS
        or s.lower() in _hce.RESERVED_OTHER_LABELS
        or s_nfkc in _hce.RESERVED_OTHER_LABELS
        or s_nfkc.lower() in _hce.RESERVED_OTHER_LABELS
    )


class CategoryColorRegistry:
    """Persistent or in-memory mapping from canonical data category names to palette slot indices."""

    def __init__(self, path: Optional[os.PathLike | str] = None, *, max_slots: int = 4) -> None:
        if max_slots < 1:
            raise ValueError("max_slots must be >= 1")
        self.path: Optional[Path] = Path(path).resolve() if path is not None else None
        self.max_slots: int = int(max_slots)
        self._entities: Dict[str, Dict[str, object]] = {}
        self._aliases: Dict[str, str] = {}
        self._palette_snapshot: List[str] = list(_hce.GEPHI_QUALITATIVE_HEX[: self.max_slots])

        if self.path is not None and self.path.is_file():
            self._load()

    @classmethod
    def for_session(cls, session_dir: os.PathLike | str, *, max_slots: int = 4) -> "CategoryColorRegistry":
        s_dir = Path(session_dir).resolve()
        if not s_dir.is_dir():
            raise FileNotFoundError(f"Session directory does not exist: {s_dir}")
        return cls(s_dir / REGISTRY_FILENAME, max_slots=max_slots)

    def _load(self) -> None:
        assert self.path is not None
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"Invalid registry JSON root in {self.path}")
        raw_entities = raw.get("entities") or {}
        raw_aliases = raw.get("aliases") or {}
        snap = raw.get("palette_snapshot")
        if isinstance(snap, list) and snap:
            self._palette_snapshot = [str(x) for x in snap]
        self._entities = {}
        for k, meta in raw_entities.items():
            if not isinstance(meta, dict) or "slot" not in meta:
                continue
            entry: Dict[str, object] = {
                "slot": int(meta["slot"]),
                "hex": str(meta.get("hex") or ""),
            }
            if "first_source" in meta and meta["first_source"] is not None:
                entry["first_source"] = str(meta["first_source"])
            self._entities[str(k)] = entry
        self._aliases = {str(a): str(c) for a, c in raw_aliases.items()}

    @property
    def aliases(self) -> Dict[str, str]:
        return dict(self._aliases)

    def _live_hex(self, slot: int) -> str:
        palette = _hce.GEPHI_QUALITATIVE_HEX
        if 0 <= slot < len(palette):
            return palette[slot]
        raise IndexError(f"Palette slot {slot} out of range for active GEPHI_QUALITATIVE_HEX (len={len(palette)})")

    def _live_tint(self, slot: int) -> str:
        tints = _hce.GEPHI_LIGHT_BADGE_TINTS
        if 0 <= slot < len(tints):
            return tints[slot]
        return "#F1F5F9"

    def _used_slots(self) -> set[int]:
        return {int(meta["slot"]) for meta in self._entities.values()}

    def _next_free_slot(self) -> Optional[int]:
        used = self._used_slots()
        for slot in range(self.max_slots):
            if slot not in used:
                return slot
        return None

    def normalize_key(self, name: object) -> str:
        raw = _raw_normalize(name)
        seen = set()
        cur = raw
        while cur in self._aliases and cur not in seen:
            seen.add(cur)
            cur = self._aliases[cur]
        return cur

    def add_alias(self, alias: str, canonical: str) -> None:
        alias_key = _raw_normalize(alias)
        canon_key = _raw_normalize(canonical)
        if not alias_key or not canon_key:
            raise ValueError("Alias and canonical name must be non-empty.")
        if alias_key == canon_key:
            return
        self._aliases[alias_key] = canon_key
        self.save()

    def pin(self, name: str, slot: int) -> str:
        if isinstance(slot, bool) or not isinstance(slot, int) or not (0 <= slot < self.max_slots):
            raise ValueError(f"Slot must be an integer in [0, {self.max_slots - 1}], got {slot!r}.")
        if _is_na_marker(name) or _is_reserved_other(name):
            raise ValueError(f"Cannot pin NA or reserved 'other' label: {name!r}")
        key = self.normalize_key(name)
        for existing_key, meta in self._entities.items():
            if int(meta["slot"]) == slot and existing_key != key:
                raise ValueError(
                    f"Slot {slot} is already assigned to '{existing_key}'; cannot pin '{key}' to it."
                )
        hex_val = self._live_hex(slot)
        prev = self._entities.get(key, {})
        entry: Dict[str, object] = {"slot": slot, "hex": hex_val}
        if "first_source" in prev:
            entry["first_source"] = prev["first_source"]
        self._entities[key] = entry
        self.save()
        return hex_val

    def assign(
        self,
        names: Iterable[object],
        *,
        overflow: str = "raise",
        source: Optional[str] = None,
    ) -> Dict[str, str]:
        if overflow not in ("raise", "other"):
            raise ValueError(f"Invalid overflow policy '{overflow}'. Expected 'raise' or 'other'.")

        na_hex = _hce.GEPHI_DISCRETE_NEUTRALS["na_missing"]
        other_hex = _hce.GEPHI_DISCRETE_NEUTRALS["other_aggregated"]

        # Stage new assignments on a copy so an overflow='raise' error never leaves partial state.
        staged_entities = {k: dict(v) for k, v in self._entities.items()}
        used_slots = {int(v["slot"]) for v in staged_entities.values()}
        result: Dict[str, str] = {}
        added = False

        for raw in names:
            if raw is None:
                result["NA"] = na_hex
                continue
            raw_str = str(raw)
            stripped = raw_str.strip()
            if _is_na_marker(stripped):
                result[stripped or "NA"] = na_hex
                continue
            if _is_reserved_other(stripped):
                result[raw_str] = other_hex
                continue

            key = self.normalize_key(raw_str)
            if key in staged_entities:
                slot = int(staged_entities[key]["slot"])
                result[raw_str] = self._live_hex(slot)
                continue

            free_slot = next((s for s in range(self.max_slots) if s not in used_slots), None)
            if free_slot is None:
                if overflow == "other":
                    result[raw_str] = other_hex
                    continue
                raise RegistryFullError(
                    f"Unique category count exceeds the {self.max_slots} locked qualitative colors "
                    f"(failed on '{raw_str}'). Per color specification Rule 5 & 7.5, either confirm "
                    "expansion mode with the user first or enable Smart 4+1 aggregation "
                    "(overflow='other' / allow_top4_aggregation=True)."
                )

            used_slots.add(free_slot)
            hex_val = self._live_hex(free_slot)
            entry: Dict[str, object] = {"slot": free_slot, "hex": hex_val}
            if source is not None:
                entry["first_source"] = str(source)
            staged_entities[key] = entry
            result[raw_str] = hex_val
            added = True

        if added:
            self._entities = staged_entities
            self.save()
        return result

    def hex_for(self, name: object, default: Optional[str] = None) -> Optional[str]:
        if _is_na_marker(name):
            return _hce.GEPHI_DISCRETE_NEUTRALS["na_missing"]
        if _is_reserved_other(name):
            return _hce.GEPHI_DISCRETE_NEUTRALS["other_aggregated"]
        key = self.normalize_key(name)
        meta = self._entities.get(key)
        if meta is None:
            return default
        return self._live_hex(int(meta["slot"]))

    def tint_for(self, name: object, default: Optional[str] = None) -> Optional[str]:
        if _is_na_marker(name) or _is_reserved_other(name):
            return default if default is not None else "#F1F5F9"
        key = self.normalize_key(name)
        meta = self._entities.get(key)
        if meta is None:
            return default
        return self._live_tint(int(meta["slot"]))

    def color_map(self, names: Optional[Iterable[object]] = None) -> Dict[str, str]:
        if names is None:
            ordered = sorted(self._entities.items(), key=lambda kv: int(kv[1]["slot"]))
            return {k: self._live_hex(int(v["slot"])) for k, v in ordered}
        out: Dict[str, str] = {}
        for raw in names:
            key = "NA" if raw is None else str(raw)
            hx = self.hex_for(raw)
            if hx is not None:
                out[key] = hx
        return out

    def to_js_entity_colors(self) -> Dict[str, str]:
        ordered = sorted(self._entities.items(), key=lambda kv: int(kv[1]["slot"]))
        return {k: self._live_hex(int(v["slot"])) for k, v in ordered}

    def save(self) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._palette_snapshot = list(_hce.GEPHI_QUALITATIVE_HEX[: self.max_slots])
        ordered_entities: Dict[str, Dict[str, object]] = {}
        for k, meta in sorted(self._entities.items(), key=lambda kv: (int(kv[1]["slot"]), kv[0])):
            slot = int(meta["slot"])
            updated: Dict[str, object] = {
                "slot": slot,
                "hex": self._live_hex(slot) if 0 <= slot < len(_hce.GEPHI_QUALITATIVE_HEX) else str(meta.get("hex", "")),
            }
            if "first_source" in meta and meta["first_source"] is not None:
                updated["first_source"] = meta["first_source"]
            ordered_entities[k] = updated

        payload = {
            "schema_version": 1,
            "palette_snapshot": self._palette_snapshot,
            "entities": ordered_entities,
            "aliases": dict(sorted(self._aliases.items())),
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        fd, tmp_name = tempfile.mkstemp(prefix=".color_reg_", suffix=".tmp", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            os.replace(tmp_name, self.path)
        except Exception:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise

    def audit(self) -> List[str]:
        issues: List[str] = []
        seen_slots: Dict[int, str] = {}
        for k, meta in self._entities.items():
            slot = int(meta["slot"])
            if not (0 <= slot < self.max_slots):
                issues.append(f"Entity '{k}' has out-of-range slot {slot} (expected 0..{self.max_slots - 1}).")
            elif slot in seen_slots:
                issues.append(f"Duplicate slot {slot} shared by '{seen_slots[slot]}' and '{k}'.")
            else:
                seen_slots[slot] = k

        for alias, target in self._aliases.items():
            if target in self._aliases:
                issues.append(f"Alias chain detected: '{alias}' -> '{target}' -> '{self._aliases[target]}'.")
            elif target not in self._entities:
                issues.append(f"Alias '{alias}' points to missing entity '{target}'.")

        live_palette = list(_hce.GEPHI_QUALITATIVE_HEX[: self.max_slots])
        if self._palette_snapshot != live_palette:
            issues.append(
                f"WARN: palette_snapshot {self._palette_snapshot} differs from active GEPHI_QUALITATIVE_HEX {live_palette}."
            )
        return issues


def use_session_registry(session_dir: os.PathLike | str) -> CategoryColorRegistry:
    """Load or initialize `<session_dir>/02_color_registry.json` and activate it for this process."""
    global _ACTIVE_REGISTRY
    reg = CategoryColorRegistry.for_session(session_dir)
    _ACTIVE_REGISTRY = reg
    return reg


def get_active_registry() -> Optional[CategoryColorRegistry]:
    """Return the currently active CategoryColorRegistry, or None if unset."""
    return _ACTIVE_REGISTRY


def clear_active_registry() -> None:
    """Deactivate the process-wide CategoryColorRegistry."""
    global _ACTIVE_REGISTRY
    _ACTIVE_REGISTRY = None
