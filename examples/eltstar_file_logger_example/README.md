# eltstar-file-logger-example

<!---aigen_start-->
Example eltstar logger plugin that registers a rotating file handler on the central `eltstar` logger.

## How it works

This package declares an entry point in the `eltstar.logger` group:

```toml
[project.entry-points."eltstar.logger"]
file_handler = "eltstar_file_logger_example.plugin:setup"
```

When `logger.load_plugins()` is called, eltstar discovers this entry point and invokes `setup(logging.Logger)`, which attaches a [`RotatingFileHandler`](https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler) to the logger.

## Configuration

| Environment variable | Default     | Description                                    |
|----------------------|-------------|------------------------------------------------|
| `ELTSTAR_LOG_FILE`      | `eltstar.log`  | Path to the log file (relative or absolute).   |

Rotation triggers at **5 MB** per file, keeping up to **3** backups.

## Usage

Install the package alongside `eltstar`, then call `load_plugins()` once at startup:

```python
from eltstar.logging import logger

logger.load_plugins()   # attaches the file handler registered by this package
logger.info("eltstar is running")
```
<!---aigen_end-->
