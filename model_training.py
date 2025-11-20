import pandas as pd
import numpy as np
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

BASE_DIR = os.path.dirname(__file__)  # directory of current file
movies = pd.read_csv(os.path.join(BASE_DIR, 'tmdb_5000_movies.csv'))
credits = pd.read_csv(os.path.join(BASE_DIR, 'tmdb_5000_credits.csv'))

# Merge datasets
movies = movies.merge(credits, on='title')

# Select important columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

# Drop missing values
movies.dropna(inplace=True)

# Helper function to convert stringified lists into Python lists
def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)

def convert3(obj):
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            L.append(i['name'])
            counter += 1
        else:
            break
    return L

movies['cast'] = movies['cast'].apply(convert3)

def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L

movies['crew'] = movies['crew'].apply(fetch_director)

# Split overview into words
movies['overview'] = movies['overview'].apply(lambda x: x.split())

# Combine all relevant tags
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

# Create a new dataframe
new = movies[['movie_id', 'title', 'tags']]

# Convert list into string
new['tags'] = new['tags'].apply(lambda x: " ".join(x))
new['tags'] = new['tags'].apply(lambda x: x.lower())

# Text vectorization
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new['tags']).toarray()

# Cosine similarity matrix
similarity = cosine_similarity(vectors)

# Save for later use
pickle.dump(new, open('movies.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))
