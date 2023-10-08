from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import crud
import recommendations
import schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    get_db()


@app.get("/users/")
def get_all_users(db: Session = Depends(get_db)):
    return crud.get_all_users(db)

@app.get("/restaurants/")
def get_all_restaurants(db: Session = Depends(get_db)):
    return crud.get_all_restaurants(db)

@app.get("/ratings/")
def get_all_ratings(db: Session = Depends(get_db)):
    return crud.get_all_ratings(db)


@app.post('/restaurant')
async def add_restaurant(rest_id, rest_name, country, city, cuisine, rating, avg_cost, votes, table_booking, online_delivery, db: Session = Depends(get_db)):
    restaurant = models.RatedRestaurants(
        rest_id=rest_id,
        rest_name=rest_name,
        country=country,
        city=city,
        cuisine=cuisine,
        avg_cost=avg_cost,
        table_booking=bool(table_booking),
        online_delivery=bool(online_delivery),
        rating=rating,
        votes=votes)
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return JSONResponse(content={
        "message": "Restaurant Added!"
    })


@app.post('/rating')
async def add_rating(user_id, rest_id, rating, db: Session = Depends(get_db)):
    rating = models.UserRatedRestaurants(
        user_id=int(user_id), rest_id=int(rest_id), rating=int(rating))
    db.add(rating)
    db.commit()
    db.refresh(rating)

    return JSONResponse(content={
        "message": "Thanks for rating this restaurant!",
    })


@app.post('/user/get-cuisines')
async def get_cuisines(city, db: Session = Depends(get_db)):
    searched = await crud.get_restaurants_cuisine(city, db)
    return JSONResponse(content=searched)

@app.post("/user/login", response_class=JSONResponse)
async def create_user(request: Request, db: Session = Depends(get_db)):
    return await crud.login_user(request, db)


@app.post('/users/recommendation-by-ratings')
async def content_based_recommendation(request: Request, db: Session = Depends(get_db)):
    df = await recommendations.get_recommendations(request, db, 10)
    data = df.to_json(orient="records")
    return JSONResponse(content=data)


@app.post('/user/search-restaurants', response_class=JSONResponse)
async def search_restaurants(request: Request, db: Session = Depends(get_db)):
    searched = await crud.search_restaurants(request, db)
    data = searched.to_json(orient="records")
    return JSONResponse(content=data)

@app.post('/user/search-restaurants-by-swagger')
async def search_restaurants(city, cuisine, price, db: Session = Depends(get_db)):
    searched = await crud.search_restaurants_by_swagger(city, cuisine, price, db)
    data = searched.to_json(orient="records")
    return JSONResponse(content=data)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
