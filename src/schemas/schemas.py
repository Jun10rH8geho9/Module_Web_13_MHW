from datetime import date, datetime
from fastapi import HTTPException, status
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
from src.schemas.users import UserResponse

class ContactModel(BaseModel):
    first_name: str = Field(max_length=15)
    last_name: str = Field(max_length=15)
    email: EmailStr
    contact_number: str
    birthday: date
    additional_information: str = Optional[str]

    @field_validator('contact_number')
    @classmethod
    def validate_contact_number(cls, value: str) -> str:
    # Удаление всех символов, не являющихся цифрами
        cleaned_number = ''.join(filter(str.isdigit, value))
    
        # Проверка длины номера контакта
        if len(cleaned_number) != 10:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid contact number")
    
        return value

    @field_validator("birthday")
    @classmethod
    def validate_birthday(cls, value: date) -> date:
        if value > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid birthday.")
        return value


class ContactResponse(ContactModel):
    id: int
    user: UserResponse | None

    class Config:
        orm_mode = True

class PasswordResetRequest(BaseModel):
    email: str


class PasswordReset(BaseModel):
    token: str
    new_password: str
