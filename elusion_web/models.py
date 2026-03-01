# Database models
try:
    from database.models import Base, Key, Server
except ImportError:
    Base = None
    Key = None
    Server = None
    import logging
    logging.warning("[Elusion Web] Could not import database models")
