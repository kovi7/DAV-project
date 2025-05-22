import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

def main():
    # Load data
    france = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', usecols = ['date','lib_reg','TO','hosp','rea', 'rad','dchosp','reg_rea'])
    poland = pd.read_csv('data/poland_covid_data.csv')

    # Data preparation 
    france['date'] = pd.to_datetime(france['date'])
    france['day_of_year'] = france['date'].dt.day_of_year
    france['month_num'] = france['date'].dt.month
    france['year'] = france['date'].dt.year
    france_series = france.groupby('date')['hosp'].sum().reset_index()
    france_series['country'] = 'France'

    poland['date'] = pd.to_datetime(poland['date'])
    poland = poland.dropna(subset=['hosp_patients'])
    poland = poland[['date', 'hosp_patients']]
    poland.rename(columns={'hosp_patients': 'hosp'}, inplace=True)
    poland['country'] = 'Poland'

    # Find common dates between countries
    max_poland_date = poland['date'].max()  # Poland's data ends faster
    min_france_date = france_series['date'].min()

    start_date = max(min_france_date, poland['date'].min())
    end_date = min(max_poland_date, france_series['date'].max())

    poland_filtered = poland[(poland['date'] >= start_date) & (poland['date'] <= end_date)]
    france_filtered = france_series[(france_series['date'] >= start_date) & (france_series['date'] <= end_date)]

    # Combine two country for plotting
    combined = pd.concat([poland_filtered, france_filtered])

    # Plotting
    fig = px.line(combined,
                x='date',
                y='hosp',
                color='country',
                title='COVID-19 Hospitalizations: Poland vs France',
                labels={
                    'date': 'Data',
                    'hosp': 'Hospitalizations',
                    'country': 'Country'
                })

    fig.update_layout(
        title_text='COVID-19 Hospitalizations: Poland vs France',
        title_font=dict(size=30, weight='bold'),
        title={
            'y':0.95,
            'x':0.50,
            'xanchor': 'center',
            'yanchor': 'top'})

    fig.update_xaxes(
        title_text='Date',
        title_font=dict(size=18),
        showgrid=True,
        gridcolor='lightgray')

    fig.update_yaxes(
        title_text='Number of Hospitalizations',
        title_font=dict(size=18),
        showgrid=True,
        gridcolor='lightgray')

    fig.update_layout(
        legend=dict(
            font=dict(size=20)))

    fig.update_layout(
        plot_bgcolor='white')

    fig.write_html('plots/hosp_pol_fra_comparison.html')
    fig.show()

if __name__=='__main__':
    main()
