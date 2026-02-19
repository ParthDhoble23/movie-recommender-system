import streamlit as st
import pickle
import pandas as pd
import requests
import os
import sys

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Movie Recommender System")

# =====================================
# VERIFY PYTHON ENV (Optional Debug)
# =====================================
# Uncomment below line if you want to verify environment
#st.write("Running Python from:", sys.executable)

# =====================================
# LOAD API KEY
# =====================================
# API_KEY = os.getenv("")
API_KEY = "ENTER_YOUR_TMDB_API_KEY"


if not API_KEY:
    st.error("❌ TMDB_API_KEY environment variable not set.")
    st.stop()

# =====================================
# LOAD DATA FILES
# =====================================
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)

    similarity = pickle.load(open('similarity.pkl', 'rb'))

except Exception as e:
    st.error(f"Error loading data files: {e}")
    st.stop()

# =====================================
# CREATE REQUEST SESSION (More Stable)
# =====================================
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

# =====================================
# FETCH POSTER FUNCTION
# =====================================
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }

    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()

        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]
        else:
            print("No poster for:", movie_id)
            return "https://via.placeholder.com/500x750?text=No+Image"

    except Exception as e:
        print("Error with movie_id:", movie_id)
        print("Error:", e)
        return "https://via.placeholder.com/500x750?text=Error"


    return "https://via.placeholder.com/500x750?text=Error"

# =====================================
# RECOMMEND FUNCTION
# =====================================
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]

        movies_list = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1]
        )[1:6]

        recommended_movies = []
        recommended_posters = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(movie_id))

        return recommended_movies, recommended_posters

    except Exception as e:
        st.error(f"Recommendation error: {e}")
        return [], []

# =====================================
# STREAMLIT UI
# =====================================
selected_movie_name = st.selectbox(
    "Select a movie:",
    movies['title'].values
)

if st.button("Recommend"):

    names, posters = recommend(selected_movie_name)

    if names:
        col1, col2, col3, col4, col5 = st.columns(5)

        columns = [col1, col2, col3, col4, col5]

        for i in range(5):
            with columns[i]:
                st.text(names[i])
                st.image(posters[i])
