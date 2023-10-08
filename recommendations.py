import pandas as pd
import numpy as np
from fastapi import Request
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from crud import fetch_user_restaurant_data


data = pd.read_csv('./restaurants.csv', encoding='latin1')


async def get_recommendations(request: Request, db: Session, n: int):
    obj = await fetch_user_restaurant_data(request, db)
    restaurant_data = obj["res"]
    city = obj["city"]
    print(city)
    restaurant_data = pd.read_sql(restaurant_data.statement, restaurant_data.session.bind)
    ratings = restaurant_data['rating'].values

    text_data = restaurant_data.apply(
        lambda x: ' '.join(x.astype(str)), axis=1)

    vectorizer = TfidfVectorizer()

    df = data[data['City'] == city]
    print(df)
    # df = df.drop(columns = ['Aggregate rating'])
    df['Features'] = df.apply(lambda x: ' '.join(x.astype(str)), axis=1)

    vectorizer = TfidfVectorizer()
    feature_vectors = vectorizer.fit_transform(df['Features'])

    row_vectors = []

    for text, rating in zip(text_data, ratings):
        vector = vectorizer.transform([text])
        weighted_vector = vector.multiply(rating).toarray()
        row_vectors.append(weighted_vector)

    flattened_vector = np.mean(row_vectors, axis=0).flatten()
    flattened_vector = flattened_vector.reshape(1, -1)  # Reshape to 2D array


    similarity_scores = cosine_similarity(
        flattened_vector, feature_vectors).flatten()

    restaurant_indices = np.argsort(similarity_scores)[::-1][:n]

    recommended_restaurants = df.iloc[restaurant_indices]
    # print(recommended_restaurants.sort_values(['Aggregate rating']))

    return recommended_restaurants.sort_values(['Aggregate rating'], ascending=False)


# def search_restaurants(request: Request, db: Session):
#     user_preferences = [request['city'], request['']]
#     selected_features = ['City', 'Locality', 'Cuisines', 'Price range', 'Aggregate rating']

# # Step 3: Create a feature vector
# data['Features'] = data[selected_features].apply(lambda x: ' '.join(x.astype(str)), axis=1)

# # Step 4: Vectorize the feature vector
# vectorizer = TfidfVectorizer()
# feature_vectors = vectorizer.fit_transform(data['Features'])
# print(feature_vectors)
# # Step 5: Calculate similarity
# similarity_matrix = cosine_similarity(feature_vectors)

# # Step 6: Recommend restaurants
# def recommend_restaurants(user_preferences, top_n=5):
#     # Create a user profile based on preferences
#     user_profile = ' '.join(user_preferences)
#     user_vector = vectorizer.transform([user_profile])

#     # Calculate similarity between user profile and all restaurants
#     similarity_scores = cosine_similarity(user_vector, feature_vectors).flatten()

#     # Sort restaurants based on similarity scores
#     restaurant_indices = np.argsort(similarity_scores)[::-1][:top_n]

#     # Get top N recommended restaurants
#     recommended_restaurants = data.iloc[restaurant_indices]

#     return recommended_restaurants

# # Example usage
# user_preferences = ['New York', 'Manhattan', 'Italian', '2', '4.5']
# recommendations = recommend_restaurants(user_preferences)

# print(recommendations[['Restaurant Name', 'City', 'Cuisines', 'Aggregate rating']])


# def get_restaurants_cuisine(request: Request, db: Session):
#     for i in ['North Indian', 'Italian', 'Chinese', 'Burger', 'South Indian']:
#         df = data[i in data['Cuisine']]
