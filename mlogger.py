import logging

logger = logging.getLogger(__name__)

errorHandler = logging.FileHandler("/var/log/groot_err.log")
standardHandler = logging.FileHandler("/var/log/groot_std.log")

errorHandler.setLevel(logging.ERROR)
standardHandler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(name)s %(message)s")
errorHandler.setFormatter(formatter)
standardHandler.setFormatter(formatter)

logger.addHandler(errorHandler)
logger.addHandler(standardHandler)