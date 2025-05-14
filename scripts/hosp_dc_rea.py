import pandas as pd
import plotly.express as px

def main():
    # data
    data = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', low_memory=False)
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
    
    fig.add_vrect(x0="2020-03-17", x1="2020-05-11", 
                  fillcolor="purple", opacity=0.2, line_width=0, 
                  annotation_text="First Lockdown",annotation_position="top left")
    fig.add_vrect(x0="2020-10-30", x1="2020-12-15", 
                  fillcolor="purple", opacity=0.2, line_width=0, 
                  annotation_text="Second Lockdown",annotation_position="top left")
    fig.add_vrect(x0="2021-04-03", x1="2021-05-03", 
                  fillcolor="purple", opacity=0.2, line_width=0, 
                  annotation_text="Third Lockdown",annotation_position="top left")


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
        font = dict(size = 18)
    )
    fig.write_html('plots/hosp_dc_rea.html')
    fig.show()

if __name__ == "__main__":
    main()