import logging
import sys

logger = logging.getLogger("robot")


class BackendHandler(logging.StreamHandler):
    log_messages = []
    log_messages_display = ["", "", ""]

    def emit(self, record: logging.LogRecord):
        self.log_messages.append(self.format(record))
        self.log_messages_display.append(record.message)

    def get_new(self):
        new = self.log_messages[:]
        self.log_messages.clear()
        return new


def setupLogger(backend_handler: BackendHandler):
    global logger
    logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%d.%m.%Y %H:%M:%S'))

    backend_handler.setLevel(logging.INFO)
    backend_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', '%H:%M:%S'))

    logger.addHandler(stdout_handler)
    logger.addHandler(backend_handler)
