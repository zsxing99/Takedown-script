"""
Abstraction of sites that will be searched
"""

from abc import ABC, abstractmethod


class BaseSite(ABC):

    @abstractmethod
    def __init__(self, **config):
        pass

    @abstractmethod
    def authenticate(self, username, password, ):
        pass

    @abstractmethod
    def search(self, source, category, ):
        pass


class SiteResult(ABC):

    @abstractmethod
    def __init__(self, **config):
        pass

