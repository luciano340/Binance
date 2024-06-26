from abc import ABC, abstractmethod

class RepositoryTradeInterface(ABC):

    @abstractmethod
    def insert_position(self):
        pass

    @abstractmethod
    def find_position(self):
        pass

    @abstractmethod
    def find_all_positions(self):
        pass

    @abstractmethod
    def sell_position(self):
        pass