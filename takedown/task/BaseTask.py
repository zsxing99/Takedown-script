"""
Abstraction of task that will be executed
"""

from abc import ABC, abstractmethod


class BaseTask(ABC):

    @abstractmethod
    def __init__(self, **settings):
        pass

