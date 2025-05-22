import pandas as pd


df = pd.read_csv("data/owid-covid-data.csv")

# Choose only Poland
poland_df = df[df['location'] == 'Poland']

poland_df = poland_df[['date', 'total_cases', 'total_deaths', 'hosp_patients', 'weekly_hosp_admissions']]

poland_df.to_csv('data/poland_covid_data.csv', index=False)