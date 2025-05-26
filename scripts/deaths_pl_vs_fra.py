import pandas as pd
import plotly.express as px
 

france = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', header=0, low_memory=False)
poland = pd.read_csv('data/poland_covid_data.csv')

france['date'] = pd.to_datetime(france['date'])
france['tx_incid'] = france['tx_incid'] /100 #now it's 1 case per 100k residents

france_deaths = france.groupby('date')['incid_dchosp'].sum().reset_index()
france_deaths.columns = ['date', 'daily_deaths']
france_deaths['total_deaths'] = france_deaths['daily_deaths'].cumsum()
france_deaths['country'] = 'France'

poland['date'] = pd.to_datetime(poland['date'])
poland_deaths = poland[['date', 'total_deaths']].copy()
poland_deaths['country'] = 'Poland'

# Find common dates between countries
max_poland_date = poland_deaths['date'].max()  # Poland's data ends faster
min_france_date = france_deaths['date'].min()

start_date = max(min_france_date, poland_deaths['date'].min())
end_date = min(max_poland_date, france_deaths['date'].max())

poland_filtered = poland_deaths[(poland_deaths['date'] >= start_date) & (poland_deaths['date'] <= end_date)]
france_filtered = france_deaths[(france_deaths['date'] >= start_date) & (france_deaths['date'] <= end_date)]

# Combine two country for plotting
combined = pd.concat([poland_filtered, france_filtered])

 # Plotting
fig = px.line(combined,
            x='date',
            y='total_deaths',
            color='country',
            title='COVID-19 Deaths: Poland vs France',
            labels={
                'date': 'Data',
                'total_deaths': 'Deaths',
                'country': 'Country'
            })

fig.update_layout(
    title_text='COVID-19 Deaths (Cumulated): Poland vs France',
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
    title_text='Number of Deaths',
    title_font=dict(size=18),
    showgrid=True,
    gridcolor='lightgray')

fig.update_layout(
    legend=dict(
        font=dict(size=20)))

fig.update_layout(
    plot_bgcolor='white')

fig.update_traces(line=dict
                  (width=5))

fig.write_html('plots/deaths_pol_fra_comparison.html')
fig.show()