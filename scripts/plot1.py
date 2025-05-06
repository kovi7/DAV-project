# import plotly.express as px
import pandas as pd
from prettytable import PrettyTable
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import calendar
from plotly.subplots import make_subplots


data = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', usecols = ['date','lib_reg','TO','hosp','rea', 'rad','dchosp','reg_rea'])
data['date'] = pd.to_datetime(data['date'])
tab_by_reg = PrettyTable()
tab_by_reg.field_names = ["Region", "Hospitalizations"]

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
    # First day of month
    first_day = pd.Timestamp(f'2023-{month:02d}-01').day_of_year
    first_days.append(first_day)
    day_labels.append("1")
    
    # 15th day of month
    days_in_month = calendar.monthrange(2023, month)[1]
    if days_in_month >= 15:
        mid_day = pd.Timestamp(f'2023-{month:02d}-15').day_of_year
        mid_days.append(mid_day)
        day_labels.append("15")
    
    # Add month name
    month_names.append(calendar.month_name[month])

# Combine all day ticks
all_days = first_days + mid_days
all_day_labels = ["1"] * len(first_days) + ["15"] * len(mid_days)

# Sort days and labels together
day_ticks = [x for _, x in sorted(zip(all_days, all_day_labels))]
all_days.sort()

#month loc
month_midpoints = []
for i, first_day in enumerate(first_days):
    if i < len(first_days) - 1:
        next_month_start = first_days[i+1]
    else:
        # For December, estimate based on days in month
        next_month_start = first_day + calendar.monthrange(2023, 12)[1]
    
    midpoint = first_day + (next_month_start - first_day) // 2
    month_midpoints.append(midpoint)

# Calculate the exact range for X axis
first_day_of_year = first_days[0]  # January 1st
# Get last day of December
last_month_days = calendar.monthrange(2023, 12)[1]
last_day_of_year = pd.Timestamp(f'2023-12-{last_month_days}').day_of_year

# Add padding before January and after December (3 days each)
padding = 3
x_min = first_day_of_year - padding
x_max = last_day_of_year + padding

# Create the figure with subplots that includes a secondary x-axis
fig = make_subplots(specs=[[{"secondary_y": False}]])

# Add data traces
for trace in plot_data:
    fig.add_trace(trace)

# Main X axis settings (for months at the bottom)
fig.update_layout(xaxis1= dict(
    title=dict(text='Month', font=dict(size=20)),
    showgrid=True,
    gridcolor='rgba(200,200,200,0.3)',
    linecolor='black',
    mirror=False,
    tickangle=0,
    tickfont=dict(size=16),
    tickvals=month_midpoints,
    # Show month names
    ticktext=month_names,
    # Set range with padding
    range=[x_min, x_max]
),

    xaxis2=dict(
        title=dict(text='Day of Month', font=dict(size=20)),
        overlaying="x",
        side="top",
        showgrid=False,
        linecolor='black',
        tickvals=all_days,  # 1st and 15th of each month
        ticktext=day_ticks,  # "1" and "15" labels
        tickfont=dict(size=14),
        anchor="y",
        position=1.0,
        range=[x_min, x_max],
        ticklabelposition="inside top",
        showline=True,
        showticklabels=True
    )
)

# fig.update_layout(xaxis2= {'anchor': 'y', 'overlaying': 'x', 'side': 'top'}, yaxis_domain=[0, 0.94])
fig.data[0].update(xaxis='x2')

# Add custom shapes for month divisions
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
        title=dict(text='Number of Hospitalizations', font=dict(size=20)),
        gridcolor='rgba(200,200,200,0.3)',
        zeroline=False,
        tickfont=dict(size=16),
        tickformat=".2s"  
    ),
    legend=dict(
        title=dict(
            text="Year",
            font=dict(size=20)
        ),
        font=dict(size=16),
        itemsizing="constant"
    ),
    title=dict(
        text='Daily Hospitalizations in France by Year',
        x=0.5,
        xanchor='center',
        font=dict(size=25, weight = 'bold')
    ),
    margin=dict(l=60, r=60, t=150, b=30),  
    width=1800,
    height=900,
)

fig.show()
