### aigen_start
import logging
import os
import sys
from collections.abc import Callable
from importlib.metadata import entry_points

LoggerPlugin = Callable[[logging.Logger], None]

ELTSTAR_LOGGER_NAME = "eltstar"
ELTSTAR_LOG_LEVEL_ENV_VAR = "ELTSTAR_LOG_LEVEL"
DEFAULT_LOG_LEVEL = logging.DEBUG
STDOUT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
STDOUT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


class EltstarLogger:
    """Central logger singleton for eltstar.

    Wraps a standard :class:`logging.Logger` under the name ``"eltstar"`` and
    supports extending it at runtime via plugins discovered through the
    ``eltstar.logger`` entry point group.

    The active log level is applied to both the logger itself and every handler
    attached to it (including handlers registered by plugins), so the singleton
    acts as the single point of control for verbosity.

    **Initial level** is resolved in this order:

    1. The ``ELTSTAR_LOG_LEVEL`` environment variable (e.g. ``"INFO"``, ``"WARNING"``).
    2. :data:`DEFAULT_LOG_LEVEL` (``DEBUG``).

    Each plugin must be a callable that accepts a :class:`logging.Logger`
    and configures it (e.g. adds handlers, attaches a formatter).  Plugins
    must *not* call ``setLevel`` on the logger or its handlers — level
    management is the responsibility of the singleton.

    Example entry point declaration in a plugin's ``pyproject.toml``::

        [project.entry-points."eltstar.logger"]
        my_handler = "my_package.logging:setup"

    Where ``setup`` is a function ``(logger: logging.Logger) -> None``.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(ELTSTAR_LOGGER_NAME)
        level: int | str = os.environ.get(ELTSTAR_LOG_LEVEL_ENV_VAR) or DEFAULT_LOG_LEVEL
        self.set_level(level)

    @property
    def underlying_logger(self) -> logging.Logger:
        """Return the underlying :class:`logging.Logger` instance."""
        return self._logger

    def set_level(self, level: int | str) -> None:
        """Set the log level on the logger and all currently attached handlers.

        Accepts the same values as :meth:`logging.Logger.setLevel` —
        an integer constant (e.g. ``logging.DEBUG``) or a level-name string
        (e.g. ``"INFO"``).
        """
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)

    def setup_stdout_handler(self) -> None:
        """Attach a :class:`logging.StreamHandler` writing to ``sys.stdout``.

        The handler uses the same timestamp + level + name format as the
        file-logger plugin.  Calling this method more than once adds a
        duplicate handler, so it should only be called once at startup.
        """
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(self._logger.level)
        handler.setFormatter(logging.Formatter(fmt=STDOUT_LOG_FORMAT, datefmt=STDOUT_DATE_FORMAT))
        self._logger.addHandler(handler)

    def load_plugins(self) -> None:
        """Discover and apply all logger plugins registered via the ``eltstar.logger`` entry point group.

        After all plugins are loaded the current log level is propagated to every
        handler they may have added, ensuring consistent level control.
        """
        for entry_point in entry_points(group="eltstar.logger"):
            self._logger.debug("Loading logger plugin: %s", entry_point.name)
            plugin: LoggerPlugin = entry_point.load()
            plugin(self._logger)
        # Propagate the active level to handlers added by plugins.
        self.set_level(self._logger.level)

    # ------------------------------------------------------------------
    # Standard logging delegation
    # ------------------------------------------------------------------

    def debug(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at DEBUG level."""
        self._logger.debug(msg, *args, **kwargs)  # type: ignore

    def info(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at INFO level."""
        self._logger.info(msg, *args, **kwargs)  # type: ignore

    def warning(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at WARNING level."""
        self._logger.warning(msg, *args, **kwargs)  # type: ignore

    def error(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at ERROR level."""
        self._logger.error(msg, *args, **kwargs)  # type: ignore

    def critical(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at CRITICAL level."""
        self._logger.critical(msg, *args, **kwargs)  # type: ignore

    def exception(self, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message at ERROR level, including the current exception traceback."""
        self._logger.exception(msg, *args, **kwargs)  # type: ignore


logger = EltstarLogger()
### aigen_end
