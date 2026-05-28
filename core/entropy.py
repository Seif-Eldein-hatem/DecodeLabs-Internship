from __future__ import annotations

import math


def _charset_size(password: str) -> int:
    has_lower = any(ch.islower() for ch in password)
    has_upper = any(ch.isupper() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)
    has_symbol = any(not ch.isalnum() for ch in password)

    size = 0
    if has_lower:
        size += 26
    if has_upper:
        size += 26
    if has_digit:
        size += 10
    if has_symbol:
        size += 32
    return max(size, 1)


def calculate_entropy(password: str) -> float:
    if not password:
        return 0.0
    size = _charset_size(password)
    return len(password) * math.log2(size)


def crack_time_estimate(entropy_bits: float, guesses_per_second: float = 1e9) -> dict:
    if entropy_bits <= 0:
        seconds = 0.0
    else:
        log10_seconds = entropy_bits * math.log10(2) - math.log10(guesses_per_second)
        seconds = 10 ** log10_seconds if log10_seconds < 308 else float("inf")

    return {
        "seconds": seconds,
        "readable": format_duration(seconds),
    }


def format_duration(seconds: float) -> str:
    if seconds == float("inf"):
        return "More than centuries"
    if seconds < 60:
        return f"{seconds:.2f} seconds"

    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.2f} minutes"

    hours = minutes / 60
    if hours < 24:
        return f"{hours:.2f} hours"

    days = hours / 24
    if days < 365:
        return f"{days:.2f} days"

    years = days / 365
    if years < 100:
        return f"{years:.2f} years"

    centuries = years / 100
    return f"{centuries:.2f} centuries"
