from pydantic import BaseModel

class UserCreate(BaseModel):
    id: str
    password: str
    email: str
    nickname: str

class UserResponse(BaseModel):
    id: str
    email: str
    nickname: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    id: str
    password: str

class UserTest(BaseModel):
    id: str
    hashed_password: str
    email: str
    nickname: str