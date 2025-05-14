import pandas as pd
import plotly.express as px
import json
from urllib.request import urlopen

####do poprawy
# zmiana na właściwe parametry i zmiana nazw!!!!!!!!
#data
df = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', header=0, low_memory=False)

deaths_by_dep = df.groupby('dep')['incid_dchosp'].sum().reset_index()
deaths_by_dep.columns = ['dep', 'total_deaths']

cases_by_dep = df.groupby('dep')['tx_incid'].sum().reset_index()
cases_by_dep.columns = ['dep', 'total_cases']

merged_data = pd.merge(deaths_by_dep, cases_by_dep, on='dep')
merged_data['dep'] = merged_data['dep'].astype(str)
merged_data['dep'] = merged_data['dep'].apply(lambda x: x.zfill(2) if len(x) == 1 else x) #cheking if numers in dep are 01 instead of 1

# geojson daat
with urlopen('https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson') as response:
    france_geojson = json.load(response)

for feature in france_geojson['features']:
    feature['properties']['code'] = feature['properties']['code'].zfill(2) if len(feature['properties']['code']) == 1 else feature['properties']['code']



#API

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
for feature in france_geojson['features']:
    feature['properties']['center'] = calculate_centroid(feature['geometry'])


def format_number(num):
    if num >= 1000000:
        return f"{int(num/1000000)}M"
    elif num >= 1000:
        return f"{int(num/1000)}k"
    else:
        return f"{int(num)}"

def create_scatter_map(data, value_column, title, color_scale, mainland_only=True):
    dep_centers = {}
    for feature in france_geojson['features']:
        dep_code = feature['properties']['code']
        center = feature['properties']['center']
        dep_centers[dep_code] = center
    
    if mainland_only:
        #Metropolitan France
        mainland_deps = [d['properties']['code'] for d in france_geojson['features'] 
                        if -5 < float(d['properties']['center'][0]) < 10 and 
                        41 < float(d['properties']['center'][1]) < 52]
        filtered_data = data[data['dep'].isin(mainland_deps)].copy()
    else:
        filtered_data = data.copy()
    
    # adding lat and lon to data
    filtered_data.loc[:, 'lon'] = filtered_data['dep'].apply(lambda x: dep_centers.get(x, [0, 0])[0])
    filtered_data.loc[:, 'lat'] = filtered_data['dep'].apply(lambda x: dep_centers.get(x, [0, 0])[1])
    
    filtered_data.loc[:, 'text'] = filtered_data[value_column].apply(format_number)
    filtered_data.loc[:, 'dep_name'] = filtered_data['dep'].map(
    lambda x: df[df['dep'] == x]['lib_dep'].iloc[0] if len(df[df['dep'] == x]) > 0 else ''
)

    
    fig = px.scatter_map(
        filtered_data,
        lat="lat",
        lon="lon",
        size=value_column,
        color=value_column,
        hover_name="dep_name",
        text="text",
        size_max=40,
        zoom=5.25,
        color_continuous_scale=color_scale,
        title=title,
        center={"lat": 46.5, "lon": 2.5},
        labels={value_column: value_column.replace('_', ' ').capitalize()}

    )
    
    fig.update_traces(textposition='middle center', textfont=dict(color='black', size=13))
    

    for i, row in filtered_data.iterrows():
        fig.add_annotation(
            x=row['lon'],
            y=row['lat'],
            text=row['dep'],
            showarrow=False,
            font=dict(size=12, color="black"),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1,
            borderpad=1
        )

    fig.update_layout(
        title = {'x':0.5, 'font': {'size':23, 'weight':'bold'}},
        autosize=True,
        font = {'size':18}

    )
    
    return fig

#deaths map
death_map = create_scatter_map(
    merged_data, 
    'total_deaths', 
    'COVID-19 Total Deaths in Metropolitan France by Department', 
    'Reds'
)

# cases map
case_map = create_scatter_map(
    merged_data, 
    'total_cases', 
    'COVID-19 Total Cases per 100k residents in Metropolitan France by Department', 
    'Blues'
)

#save
death_map.write_html('plots/deaths_map.html')
case_map.write_html('plots/cases_map.html')

death_map.show()
case_map.show()
