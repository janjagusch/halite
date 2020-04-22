"""
Provides a utils method to setup the logger.
"""

from logging import _nameToLevel

from structlog import DropEvent


class EventsAppender:
    def __init__(self, events=None):
        self.events = events or []

    def __call__(self, logger, method_name, event_dict):
        self.events.append(event_dict)
        return event_dict  


class LogLevelFilter:
    
    def __init__(self, level):
        if isinstance(level, str):
            level = _nameToLevel(level)
        self.level = level
        
    def __call__(self, logger, method_name, event_dict):
        log_level = _nameToLevel.get(method_name.upper())
        if log_level and log_level < self.level:
            raise DropEvent
        return event_dict
