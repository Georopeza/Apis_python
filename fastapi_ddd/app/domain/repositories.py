from abc import ABC, abstractmethod
from typing import List

from app.domain.schemas import Book, BookCreate


class BookRepository(ABC):

    @abstractmethod
    def get_all_books(self) -> None | List[Book]:
        pass

    @abstractmethod
    def add_book(self, book: BookCreate) -> Book:
        pass
