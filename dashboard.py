import streamlit as st
import polars as pl
import os
import plotly.express as px


st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
    }
    .stMetric {
        background-color: #161616;
        border-radius: 5px;
        padding: 10px;
    }
    .stMetric label {
        color: white !important;
    }
    .stMetric div {
        color: white !important;
    }
    h1, h2, h3, .stSelectbox label {
        color: white !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #161616 !important;
    }
    .stSidebar {
        background-color: #161616 !important;
    }
    .stSidebar .stSelectbox label {
        color: #777777 !important;
    }
    .stHeader {
        background-color: #121212 !important;
    }
    header[data-testid="stHeader"] {
        background-color: #121212 !important;
    }
    .stApp > header {
        background-color: #121212 !important;
    }
    </style>
""", unsafe_allow_html=True)

# <--------------- Page Configuration --------------->

st.set_page_config(
    page_title="Spotify Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# <--------------- Page Configuration --------------->

# List all files (playlists) in "data" folder
csv_files = [f for f in os.listdir("data") if f.endswith(".csv")] # Will only list the files that ends with .csv
csv_files_clean = [f[:-4] for f in csv_files] # Remove .csv from playlist names

# <--------------- Sidebar --------------->

with st.sidebar:
    selected_file = st.selectbox("Select a playlist", csv_files_clean) # Playlist Selector

# <--------------- Sidebar --------------->

st.title(f"{selected_file}") # Main Title

if selected_file:
    df = pl.read_csv(os.path.join("data", selected_file + ".csv"))

# <--------------- Metrics --------------->

    total_songs = df.height
    avg_duration = round(df["duration_ms"].mean() / 60000, 2)
    shortest_song = df.sort("duration_ms").row(0, named=True)
    longest_song = df.sort("duration_ms", descending=True).row(0, named=True)
    newest_song = df.sort("release_date", descending=True).row(0, named=True)
    oldest_song = df.sort("release_date").row(0, named=True)

    # st.subheader("Playlist Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Songs", total_songs)
    col2.metric("Average Duration (min)", avg_duration)
    col3.metric("Shortest Song", f"{shortest_song['track_name']} - {shortest_song['artists']}")
    col4.metric("Longest Song", f"{longest_song['track_name']} - {longest_song['artists']}")

    col5, col6 = st.columns(2)
    col5.metric("Newest Song", f"{newest_song['track_name']} | {newest_song['release_date']}")
    col6.metric("Oldest Song", f"{oldest_song['track_name']} | {oldest_song['release_date']}")

# <--------------- Top 10 Artists --------------->
    artists_exp = df.select(pl.col("artists").str.split(", ")).explode("artists") # Separating artists (Artist1, Artist2) > (Artist1)
    top_artists = artists_exp.group_by("artists").count().sort("count", descending=True).head(10) # Top
    top_artists_pd = top_artists.to_pandas()
    fig_top_artists = px.bar(
        top_artists_pd,
        x="artists",
        y="count",
        color="count",
        color_continuous_scale="viridis",
        title="Top 10 Artists by Song Count"
    )
    fig_top_artists.update_layout(
        plot_bgcolor='#161616',
        paper_bgcolor='#161616',
        font_color='white',
        title_font_color='white'
    )

# <--------------- Top 10 Tracks --------------->
    popular_tracks = df.sort("popularity", descending=True).head(10)
    popular_tracks_pd = popular_tracks.select(["track_name", "artists", "popularity"]).to_pandas()
    fig_pop_tracks = px.bar(
        popular_tracks_pd,
        x="track_name",
        y="popularity",
        color="popularity",
        hover_data=["artists"],
        color_continuous_scale="plasma",
        title="Top 10 Most Popular Tracks"
    )
    fig_pop_tracks.update_layout(
        plot_bgcolor='#161616',
        paper_bgcolor='#161616',
        font_color='white',
        title_font_color='white'
    )


# <--------------- Popularity by Artists --------------->
    artists_exp = df.select([
        pl.col("artists").str.split(", "),
        pl.col("popularity")
    ]).explode("artists")


    artist_popularity = (
        artists_exp.group_by("artists")
        .mean()
        .sort("popularity", descending=True)
        .head(10)
    )


    artist_popularity_pd = artist_popularity.to_pandas()

    # Plot
    fig_artist_pop = px.bar(
        artist_popularity_pd,
        x="artists",
        y="popularity",
        color="popularity",
        color_continuous_scale="magma",
        title="Average Popularity by Artist"
    )

    fig_artist_pop.update_layout(
        plot_bgcolor='#161616',
        paper_bgcolor='#161616',
        font_color='white',
        title_font_color='white'
    )

    # --- Layout charts ---
    row1_col1, row1_col2 = st.columns(2)
    row1_col1.plotly_chart(fig_top_artists, use_container_width=True, key="top_artists")
    row1_col2.plotly_chart(fig_pop_tracks, use_container_width=True, key="pop_tracks")

    st.plotly_chart(fig_artist_pop, use_container_width=True, key="artist_pop")  # Full width row



