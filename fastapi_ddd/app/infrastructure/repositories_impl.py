from sqlalchemy.orm import Session
from app.domain.schemas import Book, BookCreate
from app.domain.repositories import BookRepository
from app.infrastructure.orm import BookModel, SessionLocal

class SQLAlchemyBookRepository(BookRepository):
    def __init__(self):
        self.db: Session = SessionLocal()

    def get_all_books(self) -> list[Book]:
        books = self.db.query(BookModel).all()
        return [Book.from_orm(book) for book in books]

    def add_book(self, book: BookCreate) -> Book:
        db_book = BookModel(title=book.title, author=book.author, isbn=book.isbn)
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return Book.from_orm(db_book)
