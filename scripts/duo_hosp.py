import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# data
df = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv')
df['date']=pd.to_datetime(df['date'])

df_fr = df.groupby('date')['incid_hosp'].sum().reset_index()
df_fr = df_fr.sort_values('date')

df_fr['cum_hosp'] = df_fr['incid_hosp'].cumsum()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

# upper plot
ax1.plot(df_fr['date'], df_fr['cum_hosp'], color='orange')
ax1.set_ylabel('Cumulated hospitalizations', fontsize=16)
ax1.grid(True, which='both', linestyle=':', linewidth=0.5)
ax1.set_title('COVID-19 hospitalizations in France {} - {}'.format(        df_fr['date'].min().strftime('%d.%m.%Y'),
        df_fr['date'].max().strftime('%d.%m.%Y')
    ), fontsize=25, fontweight='bold')
ax1.get_yaxis().set_major_formatter(
    mtick.FuncFormatter(lambda x, _: f'{x/1_000}k' if x <1_000_000 else f'{int(x/1_000_000)}M')
)ax1.xaxis.set_visible(True)
ax1.tick_params(axis='both', labelsize=14)


# lower plot
ax2.bar(df_fr['date'], df_fr['incid_hosp'], color='orange', width=1)
ax2.set_ylabel('New hospitalizations', fontsize=16)
ax2.set_xlabel('Date', fontsize=16)
ax2.grid(True, which='both', linestyle=':', linewidth=0.5)
ax2.set_xlabel('Date')
ax2.get_yaxis().set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x/1000)}k'))
ax2.tick_params(axis='both', labelsize=14)


plt.tight_layout()
# plt.show()
plt.savefig('plots/hospitalizations_france.png',bbox_inches='tight')
