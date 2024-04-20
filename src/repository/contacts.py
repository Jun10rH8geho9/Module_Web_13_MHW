from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette import status

from src.schemas.schemas import ContactModel
from src.database.models import Contact,User


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> list[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    contact = Contact(first_name=body.first_name,
                      last_name=body.last_name,
                      email=body.email,
                      contact_number=body.contact_number,
                      birthday=body.birthday,
                      additional_information=body.additional_information,
                      user_id=user.id
                      )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactModel, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.contact_number = body.contact_number
        contact.birthday = body.birthday
        contact.additional_information = body.additional_information
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

# Пошук контакту за ім'ям
async def find_contact_by_first_name(first_name: str, user: User, db: Session) -> list[Contact]:
    contact = db.query(Contact).filter(and_(Contact.first_name == first_name, Contact.user_id == user.id)).all()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    else:
        return contact

# Пошук контакту за прізвищем
async def find_contact_by_last_name(contact_last_name: str, user: User, db: Session) -> list[Contact]:
    contact = db.query(Contact).filter(and_(Contact.last_name == contact_last_name, Contact.user_id == user.id)).all()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    else:
        return contact

# Пошук контакту за адресою електронної пошти
async def find_contact_by_email(contact_email: str, user: User, db: Session) -> list[Contact]:
    contact = db.query(Contact).filter(and_(Contact.email == contact_email, Contact.user_id == user.id)).all()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    else:
        return contact

async def upcoming_birthdays(current_date, to_date, skip: int, limit: int, user: User, db: Session) -> list[Contact]:
    contacts = db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()

    upcoming = []

    # Пошук в контактах по дням народження
    for contact in contacts:

        contact_birthday = (contact.birthday.month, contact.birthday.day)
        current_date = (current_date.month, current_date.day)
        to_date = (to_date.month, to_date.day)

        if current_date < contact_birthday <= to_date:
            upcoming.append(contact)

    return upcoming