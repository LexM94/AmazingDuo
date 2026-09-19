from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


_BOOL_TRUE = {"true", "1", "yes", "y"}
_BOOL_FALSE = {"false", "0", "no", "n"}


class ConfigError(Exception):
    ...


@dataclass
class MazeConfig:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool = False
    seed: Optional[int] = None


def _parse_int(key: str, raw: str) -> int:
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(
            f"Invalid value for {key}: {raw!r} is not an integer.") from exc


def _parse_bool(key: str, raw: str) -> bool:
    lowered = raw.strip().lower()
    if lowered in _BOOL_TRUE:
        return True
    elif lowered in _BOOL_FALSE:
        return False
    else:
        raise ConfigError(
            f"Invalid value for {key}, {raw!r} is not a boolean."
        )


def _parse_coordinate(key: str, raw: str) -> tuple[int, int]:
    result = raw.split(",")
    if len(result) != 2:
        raise ConfigError(
            f"Invalid value for {key}, {raw!r} (expected format 'x, y')."
        )
    x = _parse_int(key, result[0])
    y = _parse_int(key, result[1])

    return x, y


def _read_pairs(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise ConfigError(f"Configuration file not found: {path}") from e
    pairs: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == "" or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(f"Malformed line (expected KEY=VALUE): {raw_line!r}")
        key, _, value = line.partition("=")
        pairs[key] = value
    return pairs


def load_config(path: str) -> MazeConfig:
    file_path = Path(path)
    pairs = _read_pairs(file_path)

    mandatory = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE"}
    missing = mandatory - pairs.keys()
    if missing:
        raise ConfigError(f"Missing mandatory key(s): {missing}")
    width = _parse_int("WIDTH", pairs["WIDTH"])
    height = _parse_int("HEIGHT", pairs["HEIGHT"])

    entry = _parse_coordinate("ENTRY", pairs["ENTRY"])
    exit_ = _parse_coordinate("EXIT", pairs["EXIT"])

    x, y = entry
    if not (0 <= x < width and 0 <= y < height):
        raise ConfigError(f"Entry error: {x} or {y} is out of field.")

    a, b = exit_
    if not (0 <= a < width and 0 <= b < height):
        raise ConfigError(f"Exit error: {a} or {b} not in range")

    if entry == exit_:
        raise ConfigError(f"{entry} or {exit_} is similar")

    output_file = pairs["OUTPUT_FILE"]
    perfect = _parse_bool("PERFECT", pairs["PERFECT"]) if "PERFECT" in pairs else False

    return MazeConfig(width, height, entry, exit_, output_file, perfect)