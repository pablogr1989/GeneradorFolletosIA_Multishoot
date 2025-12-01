import logging
import sys
import os
from datetime import datetime


def setup_logger(name="brochure_generator", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d-%H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Calcular path sin importar utils
    current_file = os.path.abspath(__file__)
    utils_dir = os.path.dirname(current_file)
    src_dir = os.path.dirname(utils_dir)
    project_root = os.path.dirname(src_dir)
    date = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = os.path.join(project_root, "outputs", f"{date}.log")
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


logger = setup_logger()