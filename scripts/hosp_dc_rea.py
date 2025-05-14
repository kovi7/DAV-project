import pandas as pd
import plotly.express as px

def main():
    # data
    data = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv')
    data['date'] = pd.to_datetime(data['date'])

    #gouping by week
    data['week'] = data['date'].dt.to_period('W').apply(lambda r: r.start_time)

    columns_to_plot = ['incid_dchosp', 'incid_hosp', 'incid_rea']
    data = data.groupby('week', as_index=False)[columns_to_plot].sum()

    data_long = data.melt(id_vars='week', value_vars=columns_to_plot, 
                          var_name='Category', value_name='Value')

    category_labels = {
        'incid_dchosp': 'Deaths',
        'incid_hosp': 'Hospitalisations',
        'incid_rea': 'Reanimations'
    }
    data_long['Category'] = data_long['Category'].map(category_labels)

    fig = px.line(
        data_long,
        x='week',
        y='Value',
        color='Category', 
        labels={
            'week': 'Date'
        }
    )

    fig.update_layout(
        xaxis=dict(
            title=dict(text='Date', font=dict(size=25)),
            tickfont=dict(size=18),
        ),
        yaxis=dict(
            title=dict(text='Number', font=dict(size=25)),
            tickfont=dict(size=18),
            tickformat=".2s"
        ),
        legend=dict(
            title=dict(
                font=dict(size=20)
            ),
            font=dict(size=16),
            itemsizing="constant",
        ),
        title=dict(
            text='Weekly number of new hospitalisations, deaths and reanimations in France',
            font=dict(size=30, weight='bold'),
            x=0.5,
            xanchor='center',
        ),
    )
    fig.write_html('plots/hosp_dc_rea.html')
    fig.show()

if __name__ == "__main__":
    main()