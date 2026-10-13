### aigen_start
import logging
import logging.handlers
import os
from pathlib import Path

DEFAULT_LOG_FILE = Path("eltstar.log")
DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
DEFAULT_BACKUP_COUNT = 3
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def setup(eltstar_logger: logging.Logger) -> None:
    """Register a :class:`~logging.handlers.RotatingFileHandler` on the eltstar logger.

    The log file path is read from the ``ELTSTAR_LOG_FILE`` environment variable.
    When the variable is not set, :data:`DEFAULT_LOG_FILE` (``eltstar.log`` in the
    current working directory) is used.

    Rotation is triggered once the file reaches :data:`DEFAULT_MAX_BYTES` (5 MB),
    and up to :data:`DEFAULT_BACKUP_COUNT` (3) backup files are kept.
    """
    log_file = Path(os.environ.get("ELTSTAR_LOG_FILE", str(DEFAULT_LOG_FILE)))

    handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=DEFAULT_MAX_BYTES,
        backupCount=DEFAULT_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))

    eltstar_logger.addHandler(handler)


### aigen_end
