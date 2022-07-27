import time
from loguru import logger
from pathlib import Path

project_path = Path.cwd()
log_path = Path(project_path, "log")
t = time.strftime("%Y_%m_%d")
# format = "[{time:YYYY-MM-DD HH:mm:ss}|{level:<8}|{file}:{line}] {message}"
format = "[{time:YYYY-MM-DD HH:mm:ss}{message}"


class Loggings():
    __instance = None
    logger.add(f"{log_path}/{t}.log", rotation="500MB", encoding="utf-8", enqueue=True, format=format)

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Loggings, cls).__new__(cls, *args, **kwargs)
            return cls.__instance

    def info(self, msg):
        return logger.info(msg)

    def debug(self, msg):
        return logger.debug(msg)

    def warning(self, msg):
        return logger.warning(msg)

    def error(self, msg):
        return logger.error(msg)


log = Loggings()


if __name__ == '__main__':
    log = Loggings()
    log.info("中文test")
    log.debug("中文test")
    log.warning("中文test")
    log.error("中文test")
    logger.info('If you are using Python {}, prefer {feature} of course!', 3.6, feature='f-strings')
    n1 = "cool"
    n2 = [1, 2, 3]
    logger.info(f'If you are using Python {n1}, prefer {n2} of course!')