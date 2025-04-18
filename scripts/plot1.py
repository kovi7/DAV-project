import plotly.express as px
import pandas as pd

data = pd.read_csv('data/covid-hosp-txad-reg-2023-06-30-16h29.csv', sep=';')
metadata = pd.read_csv('data/metadata_departements-france.csv')

# print(data.head())
# print(metadata.head())
print(data['reg'].unique())
code_reg = metadata['code_region'].unique()

regions = {int(region): metadata[metadata['code_region'] == region]['nom_region'].values[0] for region in code_reg}
print("Regions: ", regions)
print(regions[1])

data['region_name'] = data['reg'].map(regions)
print(data.head())

