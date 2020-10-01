"""
Abstraction of sites that will be searched
"""

from abc import ABC, abstractmethod


class BaseSite(ABC):

    @abstractmethod
    def __init__(self, **config):
        pass

    @abstractmethod
    def authenticate(self, **config):
        pass

    @abstractmethod
    def search(self, **config):
        pass


class SiteResult(ABC):

    @abstractmethod
    def __init__(self, **config):
        pass

    @abstractmethod
    def generate_list(self, **config):
        pass

