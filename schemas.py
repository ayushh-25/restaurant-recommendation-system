from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    city: str
    email: str
    password: str

    class Config:
        orm_mode = True


class RatedRestaurants(BaseModel):
    rest_id: int
    rest_name: str
    country: str
    city: str
    cuisine: str
    avg_cost: int
    table_booking: bool
    online_delivery: bool
    rating: float
    votes: int

    class Config:
        orm_mode = True


class UserRatedRestaurants(BaseModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    rest_id: int
    rating: float

    class Config:
        orm_mode = True
