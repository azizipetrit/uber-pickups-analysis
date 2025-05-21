import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import yaml
from utils import load_data, get_day_order

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Set page config
st.set_page_config(
    page_title=config['app']['title'], 
    page_icon=config['app']['favicon'],
    layout=config['app']['layout']
)

# Sidebar for navigation and filters
st.sidebar.title("Uber Pickups Analysis")
page = st.sidebar.radio("Navigate", ["Overview", "Data Explorer", "Time Analysis", "Location Analysis"])

# Constants from utils
from utils import DATE_COLUMN

# Load data once at the beginning
data_load_state = st.sidebar.text('Loading data...')
data = load_data(config['data']['max_rows'])
data_load_state.text("Done! (using st.cache_data)")

# Main page content based on navigation
if page == "Overview":
    st.title("Uber Pickups in NYC")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("About this app")
        st.write("""
        This application visualizes Uber pickup data in New York City from September 2014.
        Use the sidebar to navigate between different analysis views.
        """)
        
        total_rides = len(data)
        st.metric("Total Rides", f"{total_rides:,}")
    
    with col2:
        st.subheader("Peak Hours")
        hist_values = np.histogram(data['hour'], bins=24, range=(0,24))[0]
        st.bar_chart(hist_values)
    
    st.subheader("Sample Data")
    if st.checkbox('Show raw data sample'):
        st.write(data.head(10))
    
elif page == "Data Explorer":
    st.title("Data Explorer")
    
    # Filter options
    st.subheader("Filter Data")
    col1, col2 = st.columns(2)
    
    with col1:
        hour_filter = st.slider("Hour of day", 0, 23)
    with col2:
        day_filter = st.multiselect("Day of week", options=sorted(data['day_of_week'].unique()))
    
    # Apply filters
    filtered_data = data
    if hour_filter:
        filtered_data = filtered_data[filtered_data['hour'] == hour_filter]
    if day_filter:
        filtered_data = filtered_data[filtered_data['day_of_week'].isin(day_filter)]
    
    # Show filtered data
    st.write(f"Filtered data - {len(filtered_data)} records")
    st.write(filtered_data)
    
    # Download CSV button
    st.download_button(
        label="Download filtered data as CSV",
        data=filtered_data.to_csv().encode('utf-8'),
        file_name='uber_pickups_filtered.csv',
        mime='text/csv',
    )

elif page == "Time Analysis":
    st.title("Time Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pickups by Hour")
        hourly_data = data.groupby('hour').size().reset_index(name='count')
        fig = px.line(hourly_data, x='hour', y='count', 
                      title='Hourly Distribution',
                      labels={'hour': 'Hour of Day', 'count': 'Number of Pickups'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Pickups by Day")
        daily_data = data.groupby('day_of_week').size().reset_index(name='count')
        # Reorder days
        day_order = get_day_order()
        daily_data['day_of_week'] = pd.Categorical(daily_data['day_of_week'], categories=day_order, ordered=True)
        daily_data = daily_data.sort_values('day_of_week')
        
        fig = px.bar(daily_data, x='day_of_week', y='count', 
                     title='Daily Distribution',
                     labels={'day_of_week': 'Day of Week', 'count': 'Number of Pickups'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap of pickups by day and hour
    st.subheader("Pickups Heatmap by Day and Hour")
    heatmap_data = data.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
    heatmap_data['day_of_week'] = pd.Categorical(heatmap_data['day_of_week'], categories=day_order, ordered=True)
    heatmap_data = heatmap_data.sort_values(['day_of_week', 'hour'])
    
    heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='count')
    fig = px.imshow(heatmap_pivot, 
                   labels=dict(x="Hour of Day", y="Day of Week", color="Pickup Count"),
                   x=[str(i) + ":00" for i in range(24)],
                   y=day_order)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

elif page == "Location Analysis":
    st.title("Location Analysis")
    
    st.subheader("Pickup Locations")
    
    hour_to_filter = st.slider('Hour', 0, 23, 17)
    st.write(f"Showing pickups at {hour_to_filter}:00")
    
    filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
    
    # Simple map
    st.subheader("Pickup Map")
    st.map(filtered_data)
    
    # 3D map with pydeck
    st.subheader("3D Visualization")
    
    # Get map settings from config
    map_config = config['map']['default_location']
    
    # Create a view of Manhattan
    view_state = pdk.ViewState(
        latitude=map_config['latitude'],
        longitude=map_config['longitude'],
        zoom=map_config['zoom'],
        pitch=map_config['pitch'],
    )
    
    # Create a hexagon layer
    hexagon_layer = pdk.Layer(
        "HexagonLayer",
        data=filtered_data,
        get_position=["lon", "lat"],
        radius=100,
        elevation_scale=4,
        elevation_range=[0, 1000],
        pickable=True,
        extruded=True,
    )
    
    # Render the deck.gl map in the Streamlit app
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[hexagon_layer],
    ))
    
    # Add density heatmap
    st.subheader("Pickup Density Heatmap")
    if len(filtered_data) > 0:  # Check that we have data to plot
        fig = px.density_mapbox(filtered_data, lat='lat', lon='lon', 
                              radius=10, zoom=10, 
                              mapbox_style="carto-positron")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data available for the selected hour.")
