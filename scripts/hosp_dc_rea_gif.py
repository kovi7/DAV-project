import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import imageio
import os

# data
file_path = 'data/table-indicateurs-open-data-france-2023-06-30-17h59.csv'
data = pd.read_csv(file_path, low_memory=False)
data['date'] = pd.to_datetime(data['date'])

#week grouping
data['week'] = data['date'].dt.to_period('W').apply(lambda r: r.start_time)
columns_to_plot = ['incid_dchosp', 'incid_hosp', 'incid_rea']
data_weekly = data.groupby('week', as_index=False)[columns_to_plot].sum()

category_labels = {
    'incid_dchosp': 'Deaths',
    'incid_hosp': 'Hospitalisations',
    'incid_rea': 'Reanimations',
}

frames = []

x_range = [data_weekly['week'].min(), data_weekly['week'].max()]
y_max = data_weekly[columns_to_plot].max().max() * 1.1 # 10% margin

# 1 plot per week
for i in range(1, len(data_weekly)+1):

    data_long = data_weekly.iloc[:i].melt(id_vars='week', value_vars=columns_to_plot, var_name='Category', value_name='Value')
    data_long['Category'] = data_long['Category'].map(category_labels)

    fig = px.line(
        data_long,
        x='week',
        y='Value',
        color='Category',
        labels={'week': 'Date'},
    )
    fig.update_xaxes(
        range=x_range,
        tickformat='%m-%Y',
        tickangle=45,
        nticks=15 
    )
    fig.update_yaxes(
        range=[0, y_max],
        tickformat='.2s',
    )
    lockdown_periods = [
        ('2020-03-17', '2020-05-11'),
        ('2020-10-30', '2020-12-15'),
        ('2021-04-03', '2021-05-03')
    ]
    for start, end in lockdown_periods:
        fig.add_vrect(x0=start, x1=end, fillcolor='purple', opacity=0.2, line_width=0)

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(color='plum', symbol='square', size=10),
        name='Lockdown'
    ))

    fig.update_layout(
        xaxis=dict(
            title=dict(text='Date', font=dict(size=25)),
            tickfont=dict(size=18),
        ),
        yaxis=dict(
            title=dict(text='Number', font=dict(size=25)),
            tickfont=dict(size=18),
            tickformat='.2s'
        ),
        legend=dict(
            title=dict(font=dict(size=20)),
            font=dict(size=16),
            itemsizing='constant',
            tracegroupgap=10,
        ),
        title=dict(
            text='Weekly number of new hospitalisations, deaths<br>and reanimations in France',
            font=dict(size=25),
            x=0.5,
            xanchor='center',
        ),
        font=dict(size=18),
        margin=dict(t=100),
        height=800,
        width=1400,
    )

    filename = f'frame_{i:03d}.png'
    fig.write_image(filename)
    frames.append(filename)

# making GIF
os.makedirs('plots', exist_ok=True)
with imageio.get_writer('plots/hosp_dc_rea.gif', mode='I', duration=0.5) as writer:
    for filename in frames:
        image = imageio.imread(filename)
        writer.append_data(image)

for filename in frames:
    os.remove(filename)

print("GIF saved as plots/hosp_dc_rea.gif")
