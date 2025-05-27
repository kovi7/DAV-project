import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from urllib.request import urlopen
import numpy as np

# Load data
df = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', header=0, low_memory=False)

# population data
pop_df = pd.read_csv('data/dep_population.csv', sep=';', header=0)
pop_df['Population totale'] = pop_df['Population totale']
pop_df['Code département'] = pop_df['Code département'].astype(str).str.zfill(2)

# Process cases data
cases_by_dep = df.groupby('dep').agg({
    'pos': 'sum',  # Total number of positive cases
    'lib_dep': 'first'  # Department name
}).reset_index()

cases_by_dep['dep'] = cases_by_dep['dep'].astype(str).str.zfill(2)
cases_by_dep = cases_by_dep.merge(
    pop_df[['Code département', 'Population totale', 'Nom du département']], 
    left_on='dep', 
    right_on='Code département', 
    how='left'
)

cases_by_dep['total_cases'] = cases_by_dep['pos']
cases_by_dep['cases_per_100k'] = (cases_by_dep['pos'] / cases_by_dep['Population totale']) * 100000

# Process deaths data
deaths_by_dep = df.groupby('dep').agg({
    'incid_dchosp': 'sum',  # Total hospital deaths
    'lib_dep': 'first'  # Department name
}).reset_index()

# Format department codes and merge with population
deaths_by_dep['dep'] = deaths_by_dep['dep'].astype(str).str.zfill(2)
deaths_by_dep = deaths_by_dep.merge(
    pop_df[['Code département', 'Population totale', 'Nom du département']], 
    left_on='dep', 
    right_on='Code département', 
    how='left'
)

deaths_by_dep['total_deaths'] = deaths_by_dep['incid_dchosp']
deaths_by_dep['deaths_per_100k'] = (deaths_by_dep['total_deaths'] / deaths_by_dep['Population totale']) * 100000

cases_by_dep = cases_by_dep.dropna(subset=['Population totale'])
deaths_by_dep = deaths_by_dep.dropna(subset=['Population totale'])

# Load GeoJSON
with urlopen('https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson') as response:
    france_geojson = json.load(response)

# Format GeoJSON codes
for feature in france_geojson['features']:
    feature['id'] = feature['properties']['code'].zfill(2)

def calculate_centroid(geometry):
    if geometry['type'] == 'Polygon':
        coords = geometry['coordinates'][0]
        x = sum(coord[0] for coord in coords) / len(coords)
        y = sum(coord[1] for coord in coords) / len(coords)
        return [x, y]
    elif geometry['type'] == 'MultiPolygon':
        largest_poly = max(geometry['coordinates'], key=lambda poly: len(poly[0]))
        coords = largest_poly[0]
        x = sum(coord[0] for coord in coords) / len(coords)
        y = sum(coord[1] for coord in coords) / len(coords)
        return [x, y]
    return [0, 0]

# Add centroids to data
dep_centers = {}
for feature in france_geojson['features']:
    dep_code = feature['id']
    center = calculate_centroid(feature['geometry'])
    dep_centers[dep_code] = center

def add_coordinates(data):
    data['lon'] = data['dep'].map(lambda x: dep_centers.get(x, [0, 0])[0])
    data['lat'] = data['dep'].map(lambda x: dep_centers.get(x, [0, 0])[1])
    return data

cases_by_dep = add_coordinates(cases_by_dep)
deaths_by_dep = add_coordinates(deaths_by_dep)

# Filter for metropolitan France only
def filter_metropolitan(data):
    return data[
        (data['lon'] > -5) & (data['lon'] < 10) & 
        (data['lat'] > 41) & (data['lat'] < 52)
    ].copy()

cases_metro = filter_metropolitan(cases_by_dep)
deaths_metro = filter_metropolitan(deaths_by_dep)

def create_choropleth_map(data, value_column, title, color_scale):
    """
    Create a choropleth map with clear department borders
    """
    fig = px.choropleth(
        data,
        geojson=france_geojson,
        locations='dep',
        color=value_column,
        featureidkey="id",
        color_continuous_scale=color_scale,
        hover_name="lib_dep",
        hover_data={
            value_column: ':,.0f' if 'total' in value_column else ':,.1f',
            'dep': True,
            'Population totale': ':,.0f'
        },
        title=title,
        labels={value_column: value_column.replace('_', ' ').title(), 'dep': 'Department code', 'Population totale': 'Total population'}
                
    )

    # Update the geographic layout to focus on France
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator"
    )


    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'font': {'size': 25, 'weight': 'bold'}

        },
        autosize=True,
        font={'size': 16},
        hoverlabel=dict(
        font_size=16)
        
    )

    
    # Make borders more visible
    fig.update_traces(
        marker_line_width=2,
        marker_line_color="white"
    )
    
    return fig

# Create maps
print("Creating COVID-19 Total Cases Map (Choropleth)...")
cases_total_map = create_choropleth_map(
    cases_metro, 
    'total_cases', 
    'COVID-19 Total Cases in Metropolitan France\nby Department',
    'Blues'
)

print("Creating COVID-19 Cases per 100k Map (Choropleth)...")
cases_per_100k_map = create_choropleth_map(
    cases_metro, 
    'cases_per_100k', 
    'COVID-19 Cases per 100k Residents in Metropolitan France\nby Department',
    'Blues'
)

print("Creating COVID-19 Total Deaths Map (Choropleth)...")
deaths_total_map = create_choropleth_map(
    deaths_metro, 
    'total_deaths', 
    'COVID-19 Total Deaths in Metropolitan France by Department',
    'Reds'
)

print("Creating COVID-19 Deaths per 100k Map (Choropleth)...")
deaths_per_100k_map = create_choropleth_map(
    deaths_metro, 
    'deaths_per_100k', 
    'COVID-19 Deaths per 100k Residents in Metropolitan France by Department',
    'Reds'
)

# Save all maps
print("Saving maps...")
cases_total_map.write_html('plots/cases_total_map.html')
cases_per_100k_map.write_html('plots/cases_per_100k_map.html')
deaths_total_map.write_html('plots/deaths_total_map.html')
deaths_per_100k_map.write_html('plots/deaths_per_100k_map.html')

print("Maps saved successfully!")
print("- Total Cases: plots/cases_total_map.html")
print("- Cases per 100k: plots/cases_per_100k_map.html")
print("- Total Deaths: plots/deaths_total_map.html")
print("- Deaths per 100k: plots/deaths_per_100k_map.html")

# Display all maps
print("Displaying maps...")
cases_total_map.show()
cases_per_100k_map.show()
deaths_total_map.show()
deaths_per_100k_map.show()

# Print summary statistics
print("\n=== SUMMARY STATISTICS ===")
print(f"Total departments processed: {len(cases_metro)}")

print("\n--- CASES ---")
max_total_cases_idx = cases_metro['total_cases'].idxmax()
max_cases_per_100k_idx = cases_metro['cases_per_100k'].idxmax()
print(f"Highest total cases: {cases_metro.loc[max_total_cases_idx, 'total_cases']:,.0f} ({cases_metro.loc[max_total_cases_idx, 'lib_dep']})")
print(f"Highest cases per 100k: {cases_metro.loc[max_cases_per_100k_idx, 'cases_per_100k']:.1f} ({cases_metro.loc[max_cases_per_100k_idx, 'lib_dep']})")

print("\n--- DEATHS ---")
max_total_deaths_idx = deaths_metro['total_deaths'].idxmax()
max_deaths_per_100k_idx = deaths_metro['deaths_per_100k'].idxmax()
print(f"Highest total deaths: {deaths_metro.loc[max_total_deaths_idx, 'total_deaths']:,.0f} ({deaths_metro.loc[max_total_deaths_idx, 'lib_dep']})")
print(f"Highest deaths per 100k: {deaths_metro.loc[max_deaths_per_100k_idx, 'deaths_per_100k']:.1f} ({deaths_metro.loc[max_deaths_per_100k_idx, 'lib_dep']})")

print(f"\nPopulation data loaded for {len(pop_df)} departments")