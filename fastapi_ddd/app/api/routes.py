from fastapi import APIRouter, Depends, HTTPException
from app.domain.services import LibraryService
from app.domain.schemas import BookCreate, Book
from app.infrastructure.repositories_impl import SQLAlchemyBookRepository


router = APIRouter()

async def get_library_service():
    repository = SQLAlchemyBookRepository()
    return LibraryService(repository)

@router.get("/books/", response_model=list[Book])
async def get_books(library_service: LibraryService = Depends(get_library_service)):
    return library_service.get_all_books()

@router.post("/books/", response_model=Book)
async def add_book(book: BookCreate, library_service: LibraryService = Depends(get_library_service)):
    return library_service.add_book(book)