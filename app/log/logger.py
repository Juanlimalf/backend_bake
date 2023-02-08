import logging


def log():
    log_format = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s'

    logging.basicConfig(level=logging.INFO,
                        format=log_format,
                        filename="log.log")

    return logging.getLogger()