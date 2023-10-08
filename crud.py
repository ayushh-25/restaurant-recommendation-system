import os
import jwt
import json
import bcrypt
from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import models
import schemas

load_dotenv()
SALT = os.getenv("SALT")
SECRET = os.getenv("SECRET")

data = pd.read_csv('./restaurants.csv', encoding='latin1')

def get_all_users(db: Session):
    records = db.query(models.User).all()
    return records

def get_all_restaurants(db: Session):
    records = db.query(models.RatedRestaurants).all()
    return records

def get_all_ratings(db: Session):
    records = db.query(models.UserRatedRestaurants).all()
    return records

def get_user_by_id(userId: int, db: Session):
    records = db.query(models.User).filter(models.User.id == userId).first()
    return records

def get_user_by_email(email, db: Session):
    user = db.query(models.User).filter(models.User.email == email).first()
    return user

async def create_user(request: Request, db: Session):
    request = await request.json()
    print(request['name'], request['city'], request['email'], request['password'])

    password = request['password'].encode('utf-8')
    salt = SALT.encode('utf-8')
    hashedPassword = bcrypt.hashpw(password, salt)
    
    encoded = jwt.encode({"email": request['email']}, SECRET, algorithm="HS256")

    user = models.User(name=request['name'], city=request['city'], email=request['email'], password=hashedPassword)
    db.add(user)
    db.commit()
    db.refresh(user)
    return JSONResponse(status_code=200, content={
            "message": "Login successful",
            "jwt": encoded
        })

async def login_user(request: Request, db: Session):
    request = await request.json()
    print(request['email'], request['password'])

    db_user = get_user_by_email(request['email'], db)
    if db_user is None:
        return JSONResponse(status_code=404, content={
            "message": "User not found"
        })

    userPassword = db_user.password.encode('utf-8')
    upHashed = bcrypt.hashpw(userPassword, SALT.encode('utf-8'))

    password = request['password'].encode('utf-8')
    reqPassHashed = bcrypt.hashpw(password, SALT.encode('utf-8'))

    encoded = jwt.encode(
        {"email": request['email']}, SECRET, algorithm="HS256")

    if bcrypt.checkpw(reqPassHashed, upHashed):
        print("Login success")
        return JSONResponse(status_code=200, content={
            "message": "Login successful",
            "jwt": encoded
        })
    else:
        print("Login failed")
        return JSONResponse(status_code=401, content={
            "message": "Login failed!"
        })


async def fetch_user_restaurant_data(request: Request, db: Session):
    request = await request.json()
    token = request['jwt'].encode('utf8')
    print(token)
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    print(decoded)
    user = db.query(models.User).filter(models.User.email == decoded['email']).first()
    rest_ids = db.query(models.UserRatedRestaurants).filter(
        models.UserRatedRestaurants.user_id == user.id)
    cols = [row.rest_id for row in rest_ids]
    print("clumns", cols, "city", user.city)
    rated_restaurants = db.query(models.RatedRestaurants).filter(
        models.RatedRestaurants.rest_id.in_(cols))
    return {"res": rated_restaurants, "city": user.city}


async def search_restaurants(request: Request, db: Session):
    request = await request.json()
    user_preferences = [request['city'], request['cuisine'], str(request['price'])]
    print(user_preferences)
    # user_preferences = [city, cuisine, price]
    # print(user_preferences)
    user_profile = ' '.join(user_preferences)
    vectorizer = TfidfVectorizer()
    selected_features = ['City', 'Cuisines',
                         'Average Cost for two']

    data['Features'] = data[selected_features].apply(
        lambda x: ' '.join(x.astype(str)), axis=1)

    feature_vectors = vectorizer.fit_transform(data['Features'])
    user_vector = vectorizer.transform([user_profile])

    similarity_scores = cosine_similarity(
        user_vector, feature_vectors).flatten()

    # Sort restaurants based on similarity scores
    restaurant_indices = np.argsort(similarity_scores)[::-1][:10]

    # Get top N recommended restaurants
    recommended_restaurants = data.iloc[restaurant_indices]

    return recommended_restaurants

async def search_restaurants_by_swagger(city, cuisine, price, db: Session):
    user_preferences = [city, cuisine, price]
    print(user_preferences)
    user_profile = ' '.join(user_preferences)
    vectorizer = TfidfVectorizer()
    selected_features = ['City', 'Cuisines', 'Average Cost for two']

    data['Features'] = data[selected_features].apply(lambda x: ' '.join(x.astype(str)), axis=1)

    feature_vectors = vectorizer.fit_transform(data['Features'])
    user_vector = vectorizer.transform([user_profile])
    

    similarity_scores = cosine_similarity(user_vector, feature_vectors).flatten()

    # Sort restaurants based on similarity scores
    restaurant_indices = np.argsort(similarity_scores)[::-1][:10]

    # Get top N recommended restaurants
    recommended_restaurants = data.iloc[restaurant_indices]

    return recommended_restaurants

async def get_restaurants_cuisine(city, db: Session):

    res = {}
    for i in ['North Indian', 'Chinese', 'Italian', 'South Indian', 'Burger']:
        df = data[data['Cuisines'].str.contains(i)]
        df = df[df['City'] == city]
        res[i] = df.to_dict(orient="records")
        res[i] = json.dumps(res[i])
    return res


# @app.get("/user/{userId}")
# def index(userId: str):
#     user = [d for d in users if d['userId'] == userId]

#     return {"user": user}

# @app.post("/user")
# def createUser(user: User):
#     return {"message": "User created successfully", "data": user}

# @app.put("/user/{userId}")
# def createUser(x_api_key : Annotated[str, Header()], userId: str, name: str):
#     print(userId, type(userId), name)
#     user = [d for d in users if d['userId'] == userId]
#     if (len(user) > 0):
#         user[0].update({"name": name})
#         return {"message": "User updated successfully", "data": user, "Api key": x_api_key}
#     else:
#         return {"message": "UserId not found"}

# @app.delete("/user/{userId}")
# def index(userId: str):
#     new_users = [d for d in users if d['userId'] != userId]

#     return {"message": "User deleted successfully", "data": new_users}
