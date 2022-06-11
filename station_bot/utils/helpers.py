import hashlib
import random
import time


def choose_color() -> int:
    return random.choice(  # nosec: B311
        (
            0x1ABC9C,
            0x11806A,
            0x2ECC71,
            0x1F8B4C,
            0x3498DB,
            0x206694,
            0x9B59B6,
            0x71368A,
            0xE91E63,
            0xAD1457,
            0xF1C40F,
            0xC27C0E,
            0xE67E22,
            0xA84300,
            0xE74C3C,
            0x992D22,
            # 0x95a5a6,
            # 0x979c9f,
            # 0x607d8b,
            # 0x546e7a,
        )
    )


def generate_id() -> str:
    return hashlib.md5(f"{time.time()}".encode(), usedforsecurity=False).hexdigest()
