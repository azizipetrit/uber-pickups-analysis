# Uber Pickups Analysis Dashboard

An interactive Streamlit dashboard that visualizes Uber pickup data in New York City for September 2014.

## Features

- **Overview**: Summary statistics and basic information about the dataset
- **Data Explorer**: Interactive filtering and data download capabilities
- **Time Analysis**: Visualizations of pickup patterns by hour and day of week
- **Location Analysis**: Interactive maps showing pickup density across NYC

## Project Structure

```text
uber_pickups/
├── app.py                # Main Streamlit app
├── utils.py              # Helper functions
├── config.yaml           # Configuration settings
├── data/                 # Place to cache data
├── assets/               # Static assets
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

1. Clone this repository
2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   streamlit run app.py
   ```

## Data Source

The data used in this dashboard comes from the Streamlit demo dataset collection and represents Uber pickups in New York City for September 2014.

## Technologies Used

- Streamlit
- Pandas
- NumPy
- Plotly
- PyDeck
- PyYAML
