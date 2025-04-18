import pandas as pd
import plotly.express as px

# Wczytaj dane
df = pd.read_csv('data/covid-hosp-txad-reg-2023-06-30-16h29.csv', sep=';', parse_dates=['jour'])
print(df.head(30))
# Regiony metropolitalne (bez wysp)
metro_codes = ['11', '24', '27', '28', '32', '44', '52', '53', '75', '76', '84', '93', '94']
region_names = {
    '11': 'Île-de-France',
    '24': 'Centre-Val de Loire',
    '27': 'Bourgogne-Franche-Comté',
    '28': 'Normandie',
    '32': 'Hauts-de-France',
    '44': 'Grand Est',
    '52': 'Pays de la Loire',
    '53': 'Brittany',
    '75': 'Nouvelle-Aquitaine',
    '76': 'Occitanie',
    '84': 'Auvergne-Rhône-Alpes',
    '93': "Provence-Alpes-Côte d'Azur",
    '94': 'Corsica'
}
df = df[df['reg'].astype(str).str.zfill(2).isin(metro_codes)]
df = df[df['PourAvec'] == 0]

# Dodaj nazwę regionu
df['region'] = df['reg'].astype(str).str.zfill(2).map(region_names)
df['month'] = df['jour'].dt.to_period('M').astype(str)

monthly = df.groupby(['month', 'region'], as_index=False)['tx_indic_7J_DC'].sum()

vmin = monthly['tx_indic_7J_DC'].min()
vmax = monthly['tx_indic_7J_DC'].max()
monthly['label'] = monthly['region'] + '<br>' + monthly['tx_indic_7J_DC'].round(1).astype(str)

region_centroids = {
    "Île-de-France": [2.5, 48.7],
    "Centre-Val de Loire": [1.7, 47.7],
    "Bourgogne-Franche-Comté": [4.7, 47.1],
    "Normandie": [0.7, 49.2],
    "Hauts-de-France": [3.0, 50.3],
    "Grand Est": [6.7, 48.5],
    "Pays de la Loire": [-0.8, 47.5],
    "Brittany": [-3.5, 48.2],
    "Nouvelle-Aquitaine": [0.2, 45.5],
    "Occitanie": [2.1, 43.8],
    "Auvergne-Rhône-Alpes": [4.5, 45.5],
    "Provence-Alpes-Côte d'Azur": [6.2, 43.8],
    "Corsica": [9.0, 42.0]
}
monthly['lon'] = monthly['region'].map(lambda x: region_centroids[x][0])
monthly['lat'] = monthly['region'].map(lambda x: region_centroids[x][1])

fig = px.choropleth(
    monthly,
    geojson="https://france-geojson.gregoiredavid.fr/repo/regions.geojson",
    locations='region',
    featureidkey="properties.nom",
    color='tx_indic_7J_DC',
    animation_frame='month',
    color_continuous_scale="Blues",
    range_color=(vmin, vmax),
    labels={'tx_indic_7J_DC': 'Monthly COVID-19 mortality'},
    title='Monthly COVID-19 Mortality in Metropolitan French Regions'
)

for month in monthly['month'].unique():
    month_data = monthly[monthly['month'] == month]
    fig.add_scattergeo(
        lon=month_data['lon'],
        lat=month_data['lat'],
        text=month_data['label'],
        mode='text',
        showlegend=False,
        row=None, col=None,
        name='',
        visible=(month == monthly['month'].unique()[0])
    )

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

fig.show()
