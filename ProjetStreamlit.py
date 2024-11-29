import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, MetaData, Table, select
import os



# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/db1')

#engine = create_engine(DATABASE_URL)
engine = create_engine(DATABASE_URL)

# Reflect the tables
metadata = MetaData()
annonces = Table('Annonce', metadata, autoload_with=engine)
villes = Table('Ville', metadata, autoload_with=engine)
equipements = Table('Equipement', metadata, autoload_with=engine)
annonce_equipements = Table('Annonce_Equipement', metadata, autoload_with=engine)

# Fetch data from the tables
def fetch_data():
    with engine.connect() as conn:
        annonces_query = conn.execute(select(annonces)).fetchall()
        villes_query = conn.execute(select(villes)).fetchall()
        equipements_query = conn.execute(select(equipements)).fetchall()
        annonce_equipements_query = conn.execute(select(annonce_equipements)).fetchall()

        annonces_df = pd.DataFrame(annonces_query, columns=annonces.columns.keys())
        villes_df = pd.DataFrame(villes_query, columns=villes.columns.keys())
        equipements_df = pd.DataFrame(equipements_query, columns=equipements.columns.keys())
        annonce_equipements_df = pd.DataFrame(annonce_equipements_query, columns=annonce_equipements.columns.keys())
    
    return annonces_df, villes_df, equipements_df, annonce_equipements_df

# Fetch data
annonces_df, villes_df, equipements_df, annonce_equipements_df = fetch_data()

# Sidebar filters
st.sidebar.header("Filters")
# Price range
min_price = annonces_df['price'].min()
max_price = annonces_df['price'].max()
price_range = st.sidebar.slider("Select Price Range", float(min_price), float(max_price), (float(min_price), float(max_price)))

# Number of rooms
min_rooms = int(annonces_df['nb_rooms'].min())
max_rooms = int(annonces_df['nb_rooms'].max())
room_range = st.sidebar.slider("Number of Rooms", min_rooms, max_rooms, (min_rooms, max_rooms))

# Number of bathrooms
min_bathrooms = int(annonces_df['num_bathrooms'].min())
max_bathrooms = int(annonces_df['num_bathrooms'].max())
bathroom_range = st.sidebar.slider("Number of Bathrooms", min_bathrooms, max_bathrooms, (min_bathrooms, max_bathrooms))

# City selection
cities = villes_df['name_ville'].unique()
selected_city = st.sidebar.selectbox("Select City", options=["All"] + list(cities))

# Equipments
available_equipments = equipements_df['name_equipement'].unique()
selected_equipments = st.sidebar.multiselect("Select Equipments", options=list(available_equipments))

# Filter data based on user input
filtered_df = annonces_df[
    (annonces_df['price'] >= price_range[0]) &
    (annonces_df['price'] <= price_range[1]) &
    (annonces_df['nb_rooms'] >= room_range[0]) &
    (annonces_df['nb_rooms'] <= room_range[1]) &
    (annonces_df['num_bathrooms'] >= bathroom_range[0]) &
    (annonces_df['num_bathrooms'] <= bathroom_range[1])
]

if selected_city != "All":
    filtered_df = filtered_df[filtered_df['city_id'] == villes_df[villes_df['name_ville'] == selected_city]['id'].values[0]]

if selected_equipments:
    filtered_announcement_ids = annonce_equipements_df[
        annonce_equipements_df['equipement_id'].isin(equipements_df[equipements_df['name_equipement'].isin(selected_equipments)]['id'])
    ]['Annonce_id'].unique()
    filtered_df = filtered_df[filtered_df['id'].isin(filtered_announcement_ids)]

# Main dashboard
st.title("Dashboard for Annonces")
st.subheader("Filtered Annonces Table")
st.dataframe(filtered_df)

import plotly.express as px
import plotly.graph_objects as go

# Main dashboard

# Bar Chart: Number of Announcements by City
st.subheader("Number of Announcements by City")
announcements_by_city = (
    filtered_df.groupby('city_id')['id'].count().reset_index().rename(columns={'id': 'count'})
)
announcements_by_city = announcements_by_city.merge(villes_df, left_on='city_id', right_on='id')
fig_bar = px.bar(
    announcements_by_city,
    x="name_ville",
    y="count",
    labels={"name_ville": "City", "count": "Number of Announcements"},
    title="Announcements Count by City"
)
st.plotly_chart(fig_bar)

# Histogram: Price Distribution
st.subheader("Price Distribution")
fig_hist = px.histogram(
    filtered_df,
    x="price",
    nbins=20,
    title="Price Distribution of Announcements",
    labels={"price": "Price"}
)
st.plotly_chart(fig_hist)

# Boxplot: Price Ranges by City
st.subheader("Price Comparison Across Cities")
price_by_city = filtered_df.merge(villes_df, left_on='city_id', right_on='id')
fig_box = px.box(
    price_by_city,
    x="name_ville",
    y="price",
    labels={"name_ville": "City", "price": "Price"},
    title="Price Ranges by City"
)
st.plotly_chart(fig_box)

# Map Visualization: Announcements by City
# Note: Ensure the Ville table includes latitude and longitude columns for map visualization.

city_coordinates = {
    "Rabat": {"latitude": 34.020882, "longitude": -6.84165},
    "Fès": {"latitude": 34.020882, "longitude": -5.00957},
    "Taghazout": {"latitude": 30.5056, "longitude": -9.6000},
    "Marrakech": {"latitude": 31.6295, "longitude": -7.9811},
    "Casablanca": {"latitude": 33.5731, "longitude": -7.5898},
    "Agadir": {"latitude": 30.4278, "longitude": -9.5981},
    "Kénitra": {"latitude": 34.2667, "longitude": -6.5667},
    "Bouskoura": {"latitude": 33.5095, "longitude": -7.6871},
    "El Jadida": {"latitude": 33.2567, "longitude": -8.5083},
    "Abdelghaya Souahel": {"latitude": 34.2500, "longitude": -6.0000},  # Approximated
    "Benslimane": {"latitude": 33.7657, "longitude": -7.2411},
    "Temara": {"latitude": 33.9167, "longitude": -6.9333},
    "Salé": {"latitude": 34.0200, "longitude": -6.8000},
    "Sidi Rahal": {"latitude": 33.3700, "longitude": -7.4800},
    "Skhirat": {"latitude": 33.8799, "longitude": -7.3478},
    "Martil": {"latitude": 35.7234, "longitude": -5.2804},
    "Taza": {"latitude": 34.2261, "longitude": -4.0057},
    "Tanger": {"latitude": 35.7667, "longitude": -5.7999},
    "Mdiq": {"latitude": 35.6914, "longitude": -5.3175},
    "Mohammedia": {"latitude": 33.6833, "longitude": -7.3833},
    "Meknès": {"latitude": 33.8977, "longitude": -5.5630},
    "Bouznika": {"latitude": 33.9578, "longitude": -7.5411},
    "Tétouan": {"latitude": 35.5755, "longitude": -5.3741},
    "Dar Bouazza": {"latitude": 33.5674, "longitude": -7.5846},
    "Urgent": {"latitude": 33.0000, "longitude": -7.0000},  # Placeholder if no city
    "Ifrane": {"latitude": 33.5320, "longitude": -5.1264},
    "Had Soualem": {"latitude": 33.2714, "longitude": -7.6607},
    "Asilah": {"latitude": 35.4678, "longitude": -6.0358},
    "Errahma": {"latitude": 33.5974, "longitude": -7.4535},
    "Oujda": {"latitude": 34.6814, "longitude": -1.9108},
    "Zenata": {"latitude": 33.7247, "longitude": -7.5856},
    "Settat": {"latitude": 32.9903, "longitude": -7.6103},
    "Sidi Allal El Bahraoui": {"latitude": 33.3205, "longitude": -6.8350},
    "Oued Laou": {"latitude": 35.2158, "longitude": -5.5670},
    "Khouribga": {"latitude": 32.8908, "longitude": -6.9075},
    "Khemisset": {"latitude": 33.6319, "longitude": -6.4203},
    "Saidia": {"latitude": 35.7606, "longitude": -2.2130},
    "Nouaceur": {"latitude": 33.3360, "longitude": -7.5864},
    "Fnideq": {"latitude": 35.2592, "longitude": -5.3502},
    "Sidi Bouknadel": {"latitude": 34.0919, "longitude": -6.7200},
    "Berrechid": {"latitude": 33.2536, "longitude": -7.5895},
    "Deroua": {"latitude": 33.3442, "longitude": -7.7625},
    "Mediouna": {"latitude": 33.5883, "longitude": -7.5711},
    "Tiznit": {"latitude": 29.6981, "longitude": -9.7347},
    "Ain Attig": {"latitude": 34.0200, "longitude": -6.7000},  # Approximated
    "Tamesna": {"latitude": 33.5000, "longitude": -7.3667},  # Approximated
    "El Mansouria": {"latitude": 33.6000, "longitude": -7.5667},  # Approximated
    "Safi": {"latitude": 32.3025, "longitude": -9.2395},
    "Berkane": {"latitude": 35.0917, "longitude": -2.3275},
    "Tamensourt": {"latitude": 31.8462, "longitude": -8.0615},
    "Nador": {"latitude": 35.1694, "longitude": -2.9306},
    "Al Hoceima": {"latitude": 35.2492, "longitude": -3.9315},
    "Essaouira": {"latitude": 31.5067, "longitude": -9.7711},
    "Biougra": {"latitude": 30.2083, "longitude": -9.3833},
    "Béni Mellal": {"latitude": 32.3333, "longitude": -6.3500},
    "Fquih Ben Saleh": {"latitude": 32.2833, "longitude": -6.3167},
    "El Kelâa des Sraghna": {"latitude": 32.0000, "longitude": -7.0000},  # Approximated
    "Larache": {"latitude": 35.1800, "longitude": -6.1400},
    "Guercif": {"latitude": 34.8000, "longitude": -3.6167},
}


# Manually add latitude and longitude to villes_df based on the city name
villes_df['latitude'] = villes_df['name_ville'].map(lambda x: city_coordinates.get(x, {}).get('latitude'))
villes_df['longitude'] = villes_df['name_ville'].map(lambda x: city_coordinates.get(x, {}).get('longitude'))

# Map Visualization: Announcements by City
if "latitude" in villes_df.columns and "longitude" in villes_df.columns:
    st.subheader("Map of Announcements by City")
    map_data = villes_df.merge(announcements_by_city, left_on="id", right_on="city_id")
    fig_map = px.scatter_mapbox(
        map_data,
        lat="latitude",
        lon="longitude",
        size="count",
        zoom=6,
        mapbox_style="open-street-map",
        title="Announcements by Location",
        labels={"name_ville": "City", "count": "Number of Announcements"}
    )
    st.plotly_chart(fig_map)
else:
    st.info("Location data (latitude and longitude) is not available for cities.")


# Scatter Plot: Surface Area vs. Price
st.subheader("Surface Area vs. Price")
if "surface_area" in filtered_df.columns and "price" in filtered_df.columns:
    fig_scatter = px.scatter(
        filtered_df,
        x="surface_area",
        y="price",
        labels={"surface_area": "Surface Area (m²)", "price": "Price"},
        title="Relationship Between Surface Area and Price"
    )
    st.plotly_chart(fig_scatter)
else:
    st.warning("Surface area or price data is not available.")


# Analyze Cities
st.subheader("Analysis of Cities")
# Bar chart: Number of annonces per city
city_counts = annonces_df.groupby('city_id').size().reset_index(name='count')
city_counts = city_counts.merge(villes_df, left_on='city_id', right_on='id', how='left')
fig_city_bar = px.bar(city_counts, x='name_ville', y='count', title="Number of Annonces per City")
st.plotly_chart(fig_city_bar)

# Price Analysis
st.subheader("Price Analysis")
# Histogram: Price distribution
fig_price_hist = px.histogram(annonces_df, x='price', nbins=20, title="Price Distribution")
st.plotly_chart(fig_price_hist)

# Boxplot: Price ranges by city
annonces_with_cities = annonces_df.merge(villes_df, left_on='city_id', right_on='id', how='left')
fig_price_box = px.box(annonces_with_cities, x='name_ville', y='price', title="Price Ranges by City")
st.plotly_chart(fig_price_box)


# Update Bar Chart: Number of Announcements by City
st.subheader("Number of Announcements by City")
announcements_by_city = (
    filtered_df.groupby('city_id')['id'].count().reset_index().rename(columns={'id': 'count'})
)
announcements_by_city = announcements_by_city.merge(villes_df, left_on='city_id', right_on='id')
fig_bar = px.bar(
    announcements_by_city,
    x="name_ville",
    y="count",
    labels={"name_ville": "City", "count": "Number of Announcements"},
    title="Announcements Count by City"
)
st.plotly_chart(fig_bar, key="bar_chart_1")

# Update Histogram: Price Distribution
st.subheader("Price Distribution")
fig_hist = px.histogram(
    filtered_df,
    x="price",
    nbins=20,
    title="Price Distribution of Announcements",
    labels={"price": "Price"}
)
st.plotly_chart(fig_hist, key="histogram_1")

# Update Boxplot: Price Ranges by City
st.subheader("Price Comparison Across Cities")
price_by_city = filtered_df.merge(villes_df, left_on='city_id', right_on='id')
fig_box = px.box(
    price_by_city,
    x="name_ville",
    y="price",
    labels={"name_ville": "City", "price": "Price"},
    title="Price Ranges by City"
)
st.plotly_chart(fig_box, key="boxplot_1")


# Update Scatter Plot: Surface Area vs. Price
st.subheader("Surface Area vs. Price")
if "surface_area" in filtered_df.columns and "price" in filtered_df.columns:
    fig_scatter = px.scatter(
        filtered_df,
        x="surface_area",
        y="price",
        labels={"surface_area": "Surface Area (m²)", "price": "Price"},
        title="Relationship Between Surface Area and Price"
    )
    st.plotly_chart(fig_scatter, key="scatter_plot_1")
else:
    st.warning("Surface area or price data is not available.")
