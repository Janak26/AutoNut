import logging

def get_logger(name: str = "my_app", log_file: str = "app.log"):
    logger = logging.getLogger(name)

    # 🔴 Always configure explicitly (do NOT rely on hasHandlers)
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs
    logger.propagate = False

    # Remove existing handlers (important in FastAPI reload)
    if logger.handlers:
        logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_file)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 🔕 Silence noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    return logger