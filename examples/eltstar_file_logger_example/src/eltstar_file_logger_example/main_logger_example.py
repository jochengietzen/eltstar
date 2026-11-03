from eltstar.logging import logger

if __name__ == "__main__":
    logger.setup_stdout_handler()
    logger.load_plugins()  # attaches the file handler registered by this package
    logger.debug("Running debug message")
    logger.info("eltstar is running with info")
    logger.warning("eltstar is running with warning")
    logger.critical("eltstar is running with critical")
    logger.error("eltstar is running with error")
