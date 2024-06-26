from app.domain.repositories import BookRepository
from app.domain.schemas import BookCreate, Book

class LibraryService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def get_all_books(self) -> list[Book]:
        return self.repository.get_all_books()

    def add_book(self, book: BookCreate) -> Book:
        return self.repository.add_book(book)