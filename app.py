import streamlit as st
import pickle
import pandas as pd
import requests


# ✅ Function to fetch poster by movie_id (always reliable)
@st.cache_data
def fetch_poster(movie_id):
    """
    Fetches a movie poster URL from TMDB API using the movie_id.
    """
    api_key = "4647fe1b545c87aaab06d2754e2445e7"  # Your TMDB API key
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Poster+Found"

    except Exception as e:
        print(f"Error fetching poster for ID {movie_id}: {e}")
        return "https://via.placeholder.com/500x750.png?text=Error"


# ✅ Recommend function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id   # <-- use movie_id directly
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# --- Main Application ---
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Error: 'movie_dict.pkl' or 'similarity.pkl' not found in directory.")
    st.stop()

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Choose a movie:',
    movies['title'].values
)

if st.button('Recommend'):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie_name)

    if names and posters:
        cols = st.columns(5)
        for col, name, poster in zip(cols, names, posters):
            with col:
                st.text(name)
                st.image(poster)