import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# data
df = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', parse_dates=['date'])

df_fr = df.groupby('date', as_index=False)['incid_rad'].sum()
df_fr = df_fr.sort_values('date')

# NA replacement
df_fr['incid_rad'] = df_fr['incid_rad'].fillna(0)

df_fr['cum_deaths'] = df_fr['incid_rad'].cumsum()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

# upper plot
ax1.plot(df_fr['date'], df_fr['cum_deaths'], color='crimson')
ax1.set_ylabel('Cumulated deaths', fontsize=16)
ax1.grid(True, which='both', linestyle=':', linewidth=0.5)
ax1.set_title(
    'COVID-19 deaths in France {} - {}'.format(
        df_fr['date'].min().strftime('%d.%m.%Y'),
        df_fr['date'].max().strftime('%d.%m.%Y')
    ),
    fontsize=25, fontweight='bold'
)
ax1.get_yaxis().set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x/1000)}k'))
ax1.xaxis.set_visible(True)
ax1.tick_params(axis='both', labelsize=14)

# lower plot
ax2.bar(df_fr['date'], df_fr['incid_rad'], color='crimson', width=1)
ax2.set_ylabel('New deaths', fontsize=16)
ax2.set_xlabel('Date', fontsize=16)
ax2.grid(True, which='both', linestyle=':', linewidth=0.5)
ax2.set_xlabel('Date')
ax2.get_yaxis().set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x/1000)}k'))
ax2.tick_params(axis='both', labelsize=14)


plt.tight_layout()
plt.savefig('plots/deaths_france.png', bbox_inches='tight')
