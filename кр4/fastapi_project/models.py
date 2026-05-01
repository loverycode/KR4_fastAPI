from sqlalchemy import Column, Integer, String, Float
from database import Base
from pydantic import BaseModel, EmailStr, constr, conint
from typing import Optional, Any

class Product(Base):
    __tablename__="products"
    id = Column( Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)
    description=Column(String, nullable=False, server_default="")

class ErrorResponse(BaseModel):
    status_code:int
    error_type: str
    message:str
    details: Optional[dict[str, Any]]=None

class User(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = 'Unknown'
