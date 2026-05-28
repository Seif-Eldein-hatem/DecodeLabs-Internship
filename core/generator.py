from __future__ import annotations

import random
import string

SYSTEM_RNG = random.SystemRandom()
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/|~"


def generate_password(
    length: int = 16,
    include_lowercase: bool = True,
    include_uppercase: bool = True,
    include_digits: bool = True,
    include_symbols: bool = True,
) -> str:
    pools = []
    if include_lowercase:
        pools.append(string.ascii_lowercase)
    if include_uppercase:
        pools.append(string.ascii_uppercase)
    if include_digits:
        pools.append(string.digits)
    if include_symbols:
        pools.append(SYMBOLS)

    if not pools:
        raise ValueError("At least one character set must be selected.")

    length = max(length, len(pools))
    password_chars = [SYSTEM_RNG.choice(pool) for pool in pools]
    all_chars = "".join(pools)
    password_chars.extend(SYSTEM_RNG.choice(all_chars) for _ in range(length - len(password_chars)))
    SYSTEM_RNG.shuffle(password_chars)
    return "".join(password_chars)
