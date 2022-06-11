__all__ = ("Config", "Database")

import logging
import typing as t
from pathlib import Path

from .config import Config
from .db import Database

__productname__ = "Station Bot"
__version__ = "0.1.0.dev0"
__description__ = "A Discord bot designed for the Metro Station Discord server."
__url__ = "https://github.com/AveraqeDev/station-bot"
__authors__ = "Matt Wagaman <smiileyface>"
__license__ = "MIT"
__bugtracker__ = "https://github.com/AveraqeDev/station-bot/issues"
__ci__ = "https://github.com/AveraqeDev/station-bot/actions"

ROOT_DIR: t.Final = Path(__file__).parent

logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
logging.getLogger("py.warnings").setLevel(logging.ERROR)
