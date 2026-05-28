from __future__ import annotations

from dataclasses import dataclass, asdict
import math
import re

from core.entropy import calculate_entropy, crack_time_estimate

COMMON_PASSWORDS = {
    "123456",
    "password",
    "qwerty",
    "admin",
    "abc123",
    "letmein",
    "welcome",
    "iloveyou",
    "111111",
    "000000",
}


@dataclass
class PasswordAnalysis:
    password: str
    score: int
    strength: str
    entropy: float
    threat_level: str
    complexity_rating: str
    crack_time: str
    crack_seconds: float
    common_password: bool
    repeated_chars: bool
    sequential_chars: bool
    has_uppercase: bool
    has_lowercase: bool
    has_numbers: bool
    has_symbols: bool
    length: int
    suggestions: list[str]
    checks: dict[str, bool]

    def to_dict(self) -> dict:
        return asdict(self)


def _has_sequential_pattern(password: str) -> bool:
    normalized = "".join(ch.lower() for ch in password if ch.isalnum())
    if len(normalized) < 3:
        return False

    for index in range(len(normalized) - 2):
        window = normalized[index : index + 3]
        if all(ord(window[i + 1]) - ord(window[i]) == 1 for i in range(2)):
            return True
        if all(ord(window[i + 1]) - ord(window[i]) == -1 for i in range(2)):
            return True
    return False


def _rate_complexity(score: int, length: int, classes: int) -> str:
    if score < 35 or length < 8:
        return "Low"
    if score < 60 or classes <= 2:
        return "Moderate"
    if score < 85:
        return "High"
    return "Elite"


def _threat_level(score: int, common: bool) -> str:
    if common or score < 35:
        return "Critical"
    if score < 60:
        return "Elevated"
    if score < 85:
        return "Guarded"
    return "Minimal"


def _strength_label(score: int) -> str:
    if score < 35:
        return "Weak"
    if score < 60:
        return "Medium"
    if score < 85:
        return "Strong"
    return "Very Strong"


def analyze_password(password: str) -> PasswordAnalysis:
    password = password or ""
    length = len(password)

    has_uppercase = any(ch.isupper() for ch in password)
    has_lowercase = any(ch.islower() for ch in password)
    has_numbers = any(ch.isdigit() for ch in password)
    has_symbols = any(not ch.isalnum() for ch in password)
    repeated_chars = bool(re.search(r"(.)\1{2,}", password))
    sequential_chars = _has_sequential_pattern(password)
    common_password = password.lower() in COMMON_PASSWORDS

    checks = {
        "Length >= 12": length >= 12,
        "Uppercase letters": has_uppercase,
        "Lowercase letters": has_lowercase,
        "Numbers": has_numbers,
        "Symbols": has_symbols,
        "No repeated characters": not repeated_chars,
        "No sequential patterns": not sequential_chars,
        "Not a common password": not common_password,
    }

    score = 0
    if length >= 8:
        score += 18
    if length >= 12:
        score += 14
    if length >= 16:
        score += 8

    classes = sum([has_uppercase, has_lowercase, has_numbers, has_symbols])
    score += classes * 12

    if repeated_chars:
        score -= 16
    if sequential_chars:
        score -= 18
    if common_password:
        score -= 45
    if length < 8:
        score -= 8

    score = max(0, min(100, score))
    entropy = calculate_entropy(password)
    crack = crack_time_estimate(entropy)

    suggestions: list[str] = []
    if length < 12:
        suggestions.append("Increase password length to at least 12 characters.")
    if not has_uppercase:
        suggestions.append("Add uppercase letters.")
    if not has_lowercase:
        suggestions.append("Add lowercase letters.")
    if not has_numbers:
        suggestions.append("Add numbers.")
    if not has_symbols:
        suggestions.append("Add symbols for better complexity.")
    if repeated_chars:
        suggestions.append("Remove repeated character patterns.")
    if sequential_chars:
        suggestions.append("Avoid sequential keyboard or number patterns.")
    if common_password:
        suggestions.append("Avoid common or leaked passwords.")

    if not suggestions:
        suggestions.append("Password structure looks strong. Consider making it longer for maximum resilience.")

    complexity = _rate_complexity(score, length, classes)
    threat = _threat_level(score, common_password)

    return PasswordAnalysis(
        password=password,
        score=score,
        strength=_strength_label(score),
        entropy=round(entropy, 2),
        threat_level=threat,
        complexity_rating=complexity,
        crack_time=crack["readable"],
        crack_seconds=crack["seconds"],
        common_password=common_password,
        repeated_chars=repeated_chars,
        sequential_chars=sequential_chars,
        has_uppercase=has_uppercase,
        has_lowercase=has_lowercase,
        has_numbers=has_numbers,
        has_symbols=has_symbols,
        length=length,
        suggestions=suggestions,
        checks=checks,
    )
