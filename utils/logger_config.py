
import os
from datetime import datetime
from logging  import getLogger, Logger, FileHandler, StreamHandler, Formatter


LOG_FILE = None
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")


class CustomFormatter(Formatter):
    def format(self, record):
        # Check if 'no_date' key is present in the record's kwargs
        if hasattr(record, 'no_date') and record.no_date:
            self._style._fmt = '%(name)s - %(levelname)s - %(message)s'
        elif hasattr(record, 'dashed') and record.dashed:
            self._style._fmt = '%(message)s'
            record.msg = f" {record.msg} ".center(85, "-")
        else:
            self._style._fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        return super().format(record)


def get_looger_file(name: str) -> str:
    """ Descobre qual arquivo o log atual está sendo salva

    Args:
        name: Logger name

    Returns:
        path do logfile
    """
    global LOG_FILE
    if LOG_FILE is None:
        os.makedirs(LOG_DIR, exist_ok=True)
        file_name = f'{name}_{os.getpid()}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        LOG_FILE = os.path.join(LOG_DIR, file_name)
        return LOG_FILE
    return LOG_FILE


def get_logger(name: str, log_to_console: bool = True, log_to_file: bool = True,
               console_level: str = "DEBUG", file_level: str = "INFO") -> Logger:
    """ Get a logger instance

    Args:
        name: Logger name
        log_to_console: if True will log to console, else logs only to file, Defaults to True
        log_to_file: file where log should be written at, Defaults to True
        console_level: Level to log at console, Defaults to DEBUG
        file_level: Level to log at file, Defaults to INFO

    Returns:
        configured logger
    """
    # Create a custom logger
    if os.path.isfile(name):
        os.path.basename(name)

    logger = getLogger(name)
    logger.setLevel("DEBUG")
    formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create file handler
    if log_to_file:
        file_handler = FileHandler(get_looger_file(name))
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Create formatters and add them to the handlers
    if log_to_console:
        console_handler = StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    # Example log messages
    logger = get_logger(__name__)
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')

    logger.info('This is an info message')
    logger.info('Without date/time', extra={'no_date': True})
    logger.info('Dashed', extra={'dashed': True})
