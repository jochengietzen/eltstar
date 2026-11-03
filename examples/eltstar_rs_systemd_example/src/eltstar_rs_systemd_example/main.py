from eltstar_rs_systemd_example.manager import manager

from eltstar.logging import logger


def main():
    logger.setup_stdout_handler()
    logger.set_level("DEBUG")
    logger.debug("Registered transformations: %s", manager._registered_transformations.keys())
    manager.execute_all_transformations()


if __name__ == "__main__":
    main()
