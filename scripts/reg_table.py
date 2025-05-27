import pandas as pd
from prettytable import PrettyTable


# data
data = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', dtype={'dep': str})

# population data
pop = pd.read_csv('data/dep_population.csv', sep=';', dtype={'Code département': str})

# dep -> region
dep_to_region = data[['dep', 'lib_reg']].drop_duplicates().set_index('dep')['lib_reg']

pop['Region'] = pop['Code département'].map(dep_to_region)

#sum population by region
region_population = pop.groupby('Region')['Population totale'].sum().reset_index()
region_population = region_population.rename(columns={'Population totale': 'Population'})

summary = data.groupby('lib_reg').agg(
    Total_Cases=pd.NamedAgg(column='pos', aggfunc='sum'),
    Total_Deaths=pd.NamedAgg(column='incid_dchosp', aggfunc='sum'),
    Vaccination_Rate=pd.NamedAgg(column='cv_dose1', aggfunc='max')
).reset_index().rename(columns={'lib_reg': 'Region'})

summary = summary.merge(region_population, on='Region', how='left')
#count cases per 100 inhabitants
summary['Cases per 100'] = (summary['Total_Cases'] / summary['Population']) * 100

summary['Total_Cases'] = summary['Total_Cases'].fillna(0).astype(int)
summary['Total_Deaths'] = summary['Total_Deaths'].fillna(0).astype(int)
summary['Vaccination_Rate'] = summary['Vaccination_Rate'].fillna('N/A')
summary['Cases per 100'] = summary['Cases per 100'].round(2)

summary = summary[['Region', 'Total_Cases', 'Cases per 100', 'Total_Deaths', 'Vaccination_Rate']]


summary.to_csv('tables/region_summary.csv', index=False)

table = PrettyTable()
table.field_names = summary.columns.tolist()
for _, row in summary.iterrows():
    table.add_row(row.tolist())
print(table)
with open('tables/region_summary.txt', 'w', encoding='utf-8') as f:
    f.write(str(table))
