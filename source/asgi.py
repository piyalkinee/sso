import sys
import logging
import signal
import time
import uvicorn.server

from gunicorn.app.base import BaseApplication
from gunicorn.arbiter import Arbiter
from gunicorn.glogging import Logger
from gunicorn import sock
from loguru import logger

from . import configuration

uvicorn.server.HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
    signal.SIGALRM,
)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class StubbedGunicornLogger(Logger):
    def setup(self, cfg):
        handler = logging.NullHandler()
        error_logger = logging.getLogger("gunicorn.error")
        error_logger.addHandler(handler)
        access_logger = logging.getLogger("gunicorn.access")
        access_logger.addHandler(handler)
        self.error_log.setLevel(self.loglevel)
        self.access_log.setLevel(self.loglevel)


class ABArbiter(Arbiter):
    def handle_int(self):
        raise StopIteration

    def stop(self, graceful=True):
        unlink = (
                self.reexec_pid == self.master_pid == 0
                and not self.systemd
                and not self.cfg.reuse_port
        )
        sock.close_sockets(self.LISTENERS, unlink)
        self.LISTENERS = []
        sig = signal.SIGALRM
        if not graceful:
            sig = signal.SIGQUIT
        limit = time.time() + self.cfg.graceful_timeout
        self.kill_workers(sig)
        while self.WORKERS and time.time() < limit:
            time.sleep(0.1)
        self.kill_workers(signal.SIGKILL)


class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

    def run(self):
        try:
            arbiter = ABArbiter(self)
            arbiter.run()
        except RuntimeError as e:
            logger.error(f"Error: {e}")
            sys.exit(1)


def start_app(app, **kwargs):
    options = kwargs if kwargs else {}
    intercept_handler = InterceptHandler()
    logging.root.setLevel(options["loglevel"])

    seen = set()

    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    _format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
              "<level>{level: <8}</level> | {process} |" \
              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:" \
              "<cyan>{line}</cyan> - <level>{message}</level>"
    logger.configure(handlers=[{"sink": sys.stdout, "serialize": 0, "format": _format}])

    StubbedGunicornLogger.loglevel = options["loglevel"]
    options = {
        "bind": "0.0.0.0:8001",
        "workers": 2,
        "access_log": "-",
        "error_log": "-",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "logger_class": StubbedGunicornLogger,
        "graceful_timeout": 30,
        "proc_name": "sso",
        **options,
    }

    StandaloneApplication(app, options).run()


def run():
    start_app(
        app="source:app",
        bind=f"{configuration.conf['api']['host']}:{configuration.conf['api']['port']}",
        workers=configuration.conf['workers'],
        proc_name="sso",
        loglevel=configuration.conf['log_level'],
        reload=configuration.conf['debug'],

    )
