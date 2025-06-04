from pydantic import BaseModel, PositiveInt
from datetime import date


class User(BaseModel):
    id: int
    nickname: str

    class Config:
        orm_mode = True


class Day(BaseModel):
    id: int
    date: date

    class Config:
        orm_mode = True


class PushUps(BaseModel):
    id: int
    user_id: int
    day_id: int

    class Config:
        orm_mode = True
