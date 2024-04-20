from datetime import date, timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Query, Path, UploadFile, File
import pathlib
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Contact, User
from src.repository import contacts as repository_contacts
from src.schemas.schemas import ContactModel, ContactResponse
from src.services.auth import auth_service
import uuid

router = APIRouter(prefix='/contacts')

# Список всіх контактів
@router.get("/", response_model=list[ContactResponse], tags=['Contacts'])
async def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts

# Контакт за ідентифікатором
@router.get("/{contact_id}", response_model=ContactResponse, tags=['Contacts'])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db), 
    current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)

    # Перевіряємо чи існує контакт
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

# Створення нового контакту
@router.post("/", response_model=ContactResponse, tags=['Contacts'], status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    contact_email = db.query(Contact).filter_by(email=body.email).first()
    contact_number = db.query(Contact).filter_by(contact_number=body.contact_number).first()
    
    # Перевіряємо існування контакту з наданною поштою
    if contact_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact with the mentioned email already exists.")
    # Перевіряємо існування контакту з наданним телефоним номером
    if contact_number:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact with the mentioned contact number already exists.")
    return await repository_contacts.create_contact(body, db)

# Оновлення існуючого контакту
@router.put("/{contact_id}", response_model=ContactResponse, tags=['Contacts'])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    contact_email = db.query(Contact).filter_by(email=body.email).first()
    contact_number = db.query(Contact).filter_by(contact_number=body.contact_number).first()

    if contact_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact with the mentioned email already exists.")

    if contact_number:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact with the mentioned contact number already exists.")
    contact = await repository_contacts.update_contact(contact_id, body, db)

    return contact


# Видалення контакту
@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, tags=['Contacts'])
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact

# Пошук контакту
@router.get("/search/", response_model=list[ContactResponse], tags=['Contacts'])
async def find_contact(contact_first_name: str = Query(None),
                       contact_last_name: str = Query(None),
                       contact_email: str = Query(None),
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    # Перевіряємо чи існує контакт з данним ім'ям
    if contact_first_name:
        return await repository_contacts.find_contact_by_first_name(contact_first_name, current_user, db)
     # Перевіряємо чи існує контакт з данним призвіщем
    elif contact_last_name:
        return await repository_contacts.find_contact_by_last_name(contact_last_name, current_user, db)
    # Перевіряємо чи існує контакт з данною поштою
    elif contact_email:
        return await repository_contacts.find_contact_by_email(contact_email, current_user, db)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You must provide at least one parameter")


# Отримання списку контактів з днями народження на найближчі 7 днів
@router.get("/birthdays/", response_model=list[ContactResponse], tags=['Birthdays'])
async def get_upcoming_birthdays(skip: int = 0, limit: int = 100,db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    current_date = date.today()
    to_date = current_date + timedelta(days=7)

    birthdays = await repository_contacts.upcoming_birthdays(current_date, to_date, skip, limit, current_user, db)
    return birthdays

# Завантаження файлу
MAX_FILE_SIZE = 1_000_000


@router.post("/upload-file/", tags=['Upload File'])
async def upload_file(file: UploadFile = File(...)):
    # Проверяем размер файла
    if file.content_length > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large, max size is {MAX_FILE_SIZE} bytes"
        )

    try:
        # Создаем папку для загрузок, если ее нет
        pathlib.Path("uploads").mkdir(exist_ok=True)

        # Генерируем уникальное имя файла
        file_uuid = str(uuid.uuid4())
        file_extension = pathlib.Path(file.filename).suffix
        file_path = f"uploads/{file_uuid}{file_extension}"

        # Сохраняем файл
        with open(file_path, "wb") as f:
            while chunk:= await file.read(1024):
                f.write(chunk)

        return {"file_path": file_path}
    except Exception as e:
        # Удаляем файл, если возникла ошибка при сохранении
        if pathlib.Path(file_path).exists():
            pathlib.Path(file_path).unlink()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))