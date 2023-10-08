from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20))
    city = Column(String(30))
    email = Column(String(100), unique=True)
    password = Column(String(100))

    # rated_restaurants = relationship(
    #     'RatedRestaurants', secondary='user_rated_restaurants', backref='users_rated')


class RatedRestaurants(Base):
    __tablename__ = 'rated_restaurants'
    rest_id = Column(Integer, primary_key=True, index=True)
    rest_name = Column(String(100))
    country = Column(String(100))
    city = Column(String(100))
    cuisine = Column(String(100))
    avg_cost = Column(Integer)
    table_booking = Column(Boolean)
    online_delivery = Column(Boolean)
    rating = Column(Float)
    votes = Column(Integer)

    # users_rated = relationship(
    #     'User', secondary='user_rated_restaurants', backref='rated_restaurants')


class UserRatedRestaurants(Base):
    __tablename__ = 'user_rated_restaurants'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    rest_id = Column(Integer, ForeignKey('rated_restaurants.rest_id'))
    rating = Column(Float)

    user = relationship('User', backref='user_rated_restaurants')
    rated_restaurants = relationship(
        'RatedRestaurants', backref='user_rated_restaurants')
