import pandas as pd
import plotly.graph_objects as go
import calendar
from plotly.subplots import make_subplots

def main():
    #data
    data = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', usecols = ['date','lib_reg','TO','hosp','rea', 'rad','dchosp','reg_rea'])
    data['date'] = pd.to_datetime(data['date'])

    data['day_of_year'] = data['date'].dt.day_of_year
    data['month_name'] = data['date'].dt.strftime('%B')
    data['month_num'] = data['date'].dt.month
    data['year'] = data['date'].dt.year

    # Group by year, month, and day
    data_by_day_month = data.groupby(['year', 'day_of_year','month_num', 'month_name'])['hosp'].sum().reset_index()

    plot_data = []
    for year, group in data_by_day_month.groupby('year'):
        plot_data.append(go.Scatter(
            x=group['day_of_year'],
            y=group['hosp'],
            mode='markers',
            name=str(year),
            marker=dict(size=8, opacity=0.7),
            showlegend=True
        ))

    first_days = []
    mid_days = []
    day_labels = []
    month_names = []

    for month in range(1, 13):
        first_day = pd.Timestamp(f'2023-{month:02d}-01').day_of_year
        first_days.append(first_day)
        day_labels.append("1")
        days_in_month = calendar.monthrange(2023, month)[1]
        if days_in_month >= 15:
            mid_day = pd.Timestamp(f'2023-{month:02d}-15').day_of_year
            mid_days.append(mid_day)
            day_labels.append("15")
        
        month_names.append(calendar.month_name[month])

    # Combine all day ticks
    all_days = first_days + mid_days
    all_day_labels = ["1"] * len(first_days) + ["15"] * len(mid_days)
    day_ticks = [x for _, x in sorted(zip(all_days, all_day_labels))]
    all_days.sort()

    #month loc
    month_midpoints = []
    for i, first_day in enumerate(first_days):
        if i < len(first_days) - 1:
            next_month_start = first_days[i+1]
        else:
            # december
            next_month_start = first_day + calendar.monthrange(2023, 12)[1]
        
        midpoint = first_day + (next_month_start - first_day) // 2
        month_midpoints.append(midpoint)

    #range for X axis
    first_day_of_year = first_days[0] 
    last_month_days = calendar.monthrange(2023, 12)[1]
    last_day_of_year = pd.Timestamp(f'2023-12-{last_month_days}').day_of_year

    padding = 3
    x_min = first_day_of_year - padding
    x_max = last_day_of_year + padding

    #second xaxis
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    for trace in plot_data:
        fig.add_trace(trace)

    fig.update_layout(xaxis1= dict(
        title=dict(text='Month', font=dict(size=25)),
        showgrid=True,
        gridcolor='rgba(200,200,200,0.3)',
        linecolor='black',
        mirror=False,
        tickangle=0,
        tickfont=dict(size=18),
        tickvals=month_midpoints,
        ticktext=month_names,
        range=[x_min, x_max]
    ),

        xaxis2=dict(
            title=dict(text='Day of Month', font=dict(size=25)),
            overlaying="x",
            side="top",
            showgrid=False,
            linecolor='black',
            tickvals=all_days, 
            ticktext=day_ticks,  # "1" and "15" labels
            tickfont=dict(size=18),
            anchor="y",
            position=1.0,
            range=[x_min, x_max],
            ticklabelposition="inside top",
            showline=True,
            showticklabels=True
        )
    )


    fig.data[0].update(xaxis='x2')

    for day in first_days[1:]: 
        fig.add_shape(
            type="line",
            x0=day, x1=day,
            y0=0, y1=1,
            yref="paper",
            line=dict(color="rgba(0,0,0,0.3)", dash='dash')
        )

    fig.update_layout(
        yaxis=dict(
            title=dict(text='Number of Hospitalizations', font=dict(size=25)),
            gridcolor='rgba(200,200,200,0.3)',
            zeroline=False,
            tickfont=dict(size=18),
            tickformat=".2s"  
        ),
        legend=dict(
            title=dict(
                text="Year",
                font=dict(size=25)
            ),
            font=dict(size=20),
            itemsizing="constant"
        ),
        title=dict(
            text='Daily Hospitalizations in France by Year',
            x=0.5,
            xanchor='center',
            font=dict(size=30, weight = 'bold')
        ),
        margin=dict(t=150, b=30),  
        width=1800,
        height=900,
    )
    fig.write_html('plots/daily_hosp.html')
    fig.show()

if __name__=='__main__':
    main()