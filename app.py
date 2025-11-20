import pandas as pd
import streamlit as st
import pickle
import requests
import os

# Correct relative data path
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# --- Function to fetch poster from TMDB ---
def fetch_poster(movie_id):
    api_key = os.getenv("TMDB_API_KEY") # your TMDB API key
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path')
    if poster_path:
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"

# --- Function to fetch movie description ---
def fetch_description(movie_id):
    api_key = os.getenv("TMDB_API_KEY") 
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()
    overview = data.get('overview', "No description available")
    return overview

# --- Recommend movies function ---
def recommend(movie, n_recommendations=10):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:n_recommendations+1]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# --- Load data ---
with open(os.path.join(DATA_PATH, 'movies_dict.pkl'), 'rb') as f:
    movies_dict = pickle.load(f)
movies = pd.DataFrame(movies_dict)

with open(os.path.join(DATA_PATH, 'similarity_dict.pkl'), 'rb') as f:
    similarity = pickle.load(f)

# --- Streamlit UI ---
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Background image using URL
import streamlit as st

background_url = "https://repository-images.githubusercontent.com/275336521/20d38e00-6634-11eb-9d1f-6a5232d0f84f"

st.markdown(
    f"""
    <style>
      .stApp {{
        background-image: url("{background_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
      }}
    </style>
    """,
    unsafe_allow_html=True
)


st.title('🎥 Movie Recommendation System')

# Movie selection
selected_movie_name = st.selectbox('Choose a movie:', movies['title'].values)
num_recommendations = st.slider('How many recommendations do you want?', 5, 20, 10)  

# Show poster and description of selected movie
movie_index = movies[movies['title'] == selected_movie_name].index[0]
movie_id = movies.iloc[movie_index].movie_id
selected_poster = fetch_poster(movie_id)
selected_description = fetch_description(movie_id)

st.subheader(f"{selected_movie_name}")
st.image(selected_poster, width=300)
st.write(selected_description)

# Recommend button
if st.button('Recommend'):
    st.subheader("Recommended Movies")
    names, posters = recommend(selected_movie_name, n_recommendations=num_recommendations)

    # Display recommended movies
    cols = st.columns(5) # 5 movies per row
    for i, (name, poster) in enumerate(zip(names, posters)):
        with cols[i % 5]:
            st.image(poster, use_container_width=True)
            st.caption(name)
        if (i + 1) % 5 == 0:
            cols = st.columns(5) # new row