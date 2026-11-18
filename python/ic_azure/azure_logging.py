"""Logging for the Zabbix Azure monitoring scripts.

The scripts are run as Zabbix passive items, so anything written to stdout or
stderr becomes the item value. All diagnostics therefore go to a log file only:

    /var/log/zabbix/scripts/zabbix_azure_monitoring/<script_name>.log

Environment variables:
    AZURE_MONITORING_LOG_DIR    Override the log directory.
    AZURE_MONITORING_LOG_LEVEL  DEBUG, INFO (default), WARNING or ERROR. DEBUG also
                                enables Azure SDK/MSAL logging.
"""

import functools
import logging
import logging.handlers
import os
import sys
import time

DEFAULT_LOG_DIR = "/var/log/zabbix/scripts/zabbix_azure_monitoring"

# Zabbix agent discards command output larger than this
ZABBIX_OUTPUT_LIMIT = 512 * 1024

# Taken at import time; scripts import this module before the Azure SDK
_IMPORT_TIME = time.monotonic()

logger = logging.getLogger("ic_azure")

_context = {}
_output = {}


class _ContextFilter(logging.Filter):
    def filter(self, record):
        record.context = " ".join(
            f"{key}={_quote(value)}" for key, value in _context.items() if value
        )
        return True


def _quote(value):
    value = str(value)
    if len(value) > 200:
        value = value[:200] + "..."
    return f'"{value}"' if " " in value else value


def setup(script_name):
    """Configure file logging. Never writes to stdout/stderr, even on failure."""

    level_name = os.getenv("AZURE_MONITORING_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    log_dir = os.getenv("AZURE_MONITORING_LOG_DIR", DEFAULT_LOG_DIR)

    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    root.setLevel(level)

    try:
        os.makedirs(log_dir, exist_ok=True)
        # WatchedFileHandler reopens the file after logrotate moves it
        handler = logging.handlers.WatchedFileHandler(
            os.path.join(log_dir, f"{script_name}.log")
        )
    except OSError:
        handler = logging.NullHandler()

    handler.setFormatter(logging.Formatter(
        "%(asctime)s pid=%(process)d %(levelname)s %(name)s [%(context)s] %(message)s"
    ))
    handler.addFilter(_ContextFilter())
    root.addHandler(handler)

    # Keep the SDK quiet unless debugging; its warnings (e.g. token cache lock) are kept
    if level > logging.DEBUG:
        for name in ("azure", "msal", "msal_extensions", "urllib3", "msrest"):
            logging.getLogger(name).setLevel(logging.WARNING)

    # Make sure nothing ends up on stderr through logging's last-resort handler
    logging.lastResort = None
    logging.raiseExceptions = False


def set_context(**kwargs):
    """Add key=value pairs to every following log line, e.g. config or metric."""
    _context.update(kwargs)


def set_resource(resource_id):
    """Add subscription, resource group and resource from an Azure resource ID."""

    if not resource_id:
        return
    parts = resource_id.strip("/").split("/")
    lower = [p.lower() for p in parts]

    def after(key, count=1):
        if key not in lower:
            return None
        return "/".join(parts[lower.index(key) + count:]) or None

    set_context(
        sub=(after("subscriptions") or "").split("/")[0],
        rg=(after("resourcegroups") or "").split("/")[0],
        # Skip the provider namespace, e.g. Microsoft.Sql, keep servers/x/databases/y
        resource=after("providers", 2)
    )


def emit(text, items=None):
    """Print the item value for Zabbix and record its size."""

    size = len(text.encode("utf-8"))
    _output["bytes"] = size
    if items is not None:
        _output["items"] = items
    if size > ZABBIX_OUTPUT_LIMIT:
        logger.warning(
            "Output is %d bytes (%s items), exceeding Zabbix agent limit of %d bytes; "
            "the agent will discard it", size, items, ZABBIX_OUTPUT_LIMIT
        )
    print(text)


def _stats(start):
    times = os.times()
    stats = (
        f"run={time.monotonic() - start:.2f}s "
        f"imports={start - _IMPORT_TIME:.2f}s "
        f"cpu={times.user + times.system:.2f}s"
    )
    for key, value in _output.items():
        stats += f" {key}={value}"
    return stats


def log_run(script_name):
    """Decorator for script main(): logs start, result, duration, CPU and failures."""

    def decorator(main):
        @functools.wraps(main)
        def wrapper(*args, **kwargs):
            setup(script_name)
            # Reserve the first position; scripts fill it from args.config after parsing
            set_context(config=None)
            start = time.monotonic()
            # A "Started" line without a result for the same pid means the agent
            # killed the process (timeout)
            logger.info("Started (imports=%.2fs)", start - _IMPORT_TIME)
            try:
                result = main(*args, **kwargs)
            except SystemExit as ex:
                if ex.code not in (None, 0):
                    logger.error(
                        "Exited with %r (%s) args=%s", ex.code, _stats(start), sys.argv[1:]
                    )
                else:
                    logger.info("OK (%s)", _stats(start))
                raise
            except BaseException:
                logger.exception("Failed (%s) args=%s", _stats(start), sys.argv[1:])
                raise
            logger.info("OK (%s)", _stats(start))
            return result
        return wrapper
    return decorator
