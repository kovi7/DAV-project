import pandas as pd
import plotly.express as px

def main():
	data = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', usecols = ['date','lib_reg','TO', 'pos'])
	data['date'] = pd.to_datetime(data['date'])

	fig = px.bar(data, x="lib_reg", y="pos", color="lib_reg",
		animation_frame="date", animation_group="lib_reg") 

	new_xticks=data["lib_reg"][:len(set(data["lib_reg"].values))].values
	fig.update_layout(
	xaxis_tickangle=0,
	xaxis=dict(
		title=dict(text='lib_reg'),
		tickfont = dict(size=18),
		tickmode = 'array',
		tickvals = [x for x in range(len(new_xticks))],
		ticktext=new_xticks
	))

	fig = px.line(data, x = 'date',y="pos", color="lib_reg",
		range_x=[data["date"].min(),data["date"].max()], labels={
            'lib_reg': 'Region',
            'pos': 'Number of new cases',
            'date': 'Date'
		})

	fig.update_layout(
		xaxis=dict(
		title=dict(text='Date', font = dict(size=25)),
		tickfont = dict(size=18),
		),
		yaxis=dict(
			title=dict(text='Number of new cases', font = dict(size=25)),
			tickfont = dict(size=18)
		),
		legend=dict(
			title=dict(
				text="Region",
				font = dict(size=20)
			),
			font=dict(size=16),
       		itemsizing="constant"
		),
		title=dict(
			text='Daily number of corfirmed new COVID-19 cases in France per Region',
			font=dict(size=30, weight='bold'),
			x=0.5,
			xanchor='center',
		),			
	)
	fig.write_html('plots/new_cases_reg.html')
	fig.show()

if __name__ == "__main__":
	main()