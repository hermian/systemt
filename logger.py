import logging

logger_initialized = False

def get_logger(name='SystemT'):
    global logger_initialized

    logger = logging.getLogger(name)

    if not logger_initialized: initialize(logger)
    return logger

def initialize(logger):
    global logger_initialized

    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
    )
    logger.addHandler(console_handler)

    logger_initialized = True