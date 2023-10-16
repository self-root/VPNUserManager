import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

handler = RotatingFileHandler("/var/log/groot/groot.log", maxBytes=1000, backupCount=1)


handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(name)s %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)