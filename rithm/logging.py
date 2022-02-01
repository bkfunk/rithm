import logging
from rich.logging import RichHandler

def get_logger(name: str): 
    logging.basicConfig(
        level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler(show_time=False, rich_tracebacks=True, markup=True)]
    )
    return logging.getLogger(name)
# log = logging.getLogger("Rithm")
