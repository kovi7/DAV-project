import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def main():
    # data
    data = pd.read_csv('data/table-indicateurs-open-data-france-2023-06-30-17h59.csv', low_memory=False)
    data['date'] = pd.to_datetime(data['date'])

    #gouping by week
    data['week'] = data['date'].dt.to_period('W').apply(lambda r: r.start_time)

    columns_to_plot = ['incid_dchosp', 'incid_hosp', 'incid_rea', ]

    data = data.groupby('week', as_index=False)[columns_to_plot].sum()

    data_long = data.melt(id_vars='week', value_vars=columns_to_plot, 
                          var_name='Category', value_name='Value')

    category_labels = {
        'incid_dchosp': 'Deaths',
        'incid_hosp': 'Hospitalisations',
        'incid_rea': 'Reanimations',
    }
    data_long['Category'] = data_long['Category'].map(category_labels)

    # Adding lockdown periods
    lockdown_periods = [
        ('2020-03-17', '2020-05-11'),
        ('2020-10-30', '2020-12-15'),
        ('2021-04-03', '2021-05-03')
    ]

    # Add a new column for lockdown status
    data_long['Lockdown'] = data_long['week'].apply(
        lambda x: 'Lockdown' if any(pd.to_datetime(start) <= x <= pd.to_datetime(end) for start, end in lockdown_periods) else 'No Lockdown'
    )

    # Plotting
    fig = px.line(
        data_long,
        x='week',
        y='Value',
        color='Category', 
        labels={
            'week': 'Date'
        }
    )
    
    # Add vertical rects for lockdown periods
    for start, end in lockdown_periods:
        fig.add_vrect(x0=start, x1=end, 
                      fillcolor="purple", opacity=0.2, line_width=0)
    
    # Add a fake trace for the lockdown in the legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None], 
        mode='markers',
        marker=dict(color="plum", symbol="square", size=10),
        name="Lockdown"
    ))

    # Customize layout
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
            tracegroupgap=10,  # Optional: To make the legend items spaced out
        ),
        title=dict(
            text='Weekly number of new hospitalisations, deaths<br>and reanimations in France',
            font=dict(size=30, weight='bold'),
            x=0.5,
            xanchor='center',
        ),
        font = dict(size = 18),
        margin=dict(t=100),
    )

    fig.write_html('plots/hosp_dc_rea.html')
    fig.show()

if __name__ == "__main__":
    main()
