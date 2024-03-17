import logging


def setup_custom_logger(name):
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[handler])
    logger = logging.getLogger(name)
    return logger
