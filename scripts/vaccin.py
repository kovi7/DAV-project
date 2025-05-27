import matplotlib.pyplot as plt
import pandas as pd
from pywaffle import Waffle

def main():
    df = pd.read_csv('data/vacsi-tot-s-fra-2023-07-13-15h51.csv', sep=';')
    data = df[df['sexe'] == 0].iloc[0]

    total_population = 100  
    booster = float(data['couv_tot_rappel'])
    complete_no_booster = round(float(data['couv_tot_complet'] - data['couv_tot_rappel']))
    incomplete = round(float(data['couv_tot_dose1'] - data['couv_tot_complet']),2)
    not_vaccinated = round(float(total_population - data['couv_tot_dose1']))

    vaccination_data = {
        'Complete primary series + booster shot': booster,
        'Complete primary series without booster shot': complete_no_booster,
        'Incomplete primary series': incomplete,
        'Not vaccinated': not_vaccinated
    }

    colors = [
        '#FF9EC3',
        '#FF69B4',
        '#8B0000',
        '#CCCCCC'
    ]

    # Oblicz wartości procentowe dla legendy
    total = sum(vaccination_data.values())
    vaccination_data_percent = {
        f"{key} ({value}%)": value for key, value in vaccination_data.items()
    }

    fig = plt.figure(
        FigureClass=Waffle,
        rows=5, 
        columns=20, 
        values=vaccination_data_percent,
        colors=colors,
        icons='male',
        icon_size=40, 
        icon_legend=True,
        legend={
            'bbox_to_anchor': (1, -0.1), 
            'ncol': 1,
            'framealpha': 0.5, 
            'fontsize': 12 
        }, 
        figsize=(12, 6)
    )
    plt.title('COVID-19 vaccination coverage in France', size = 30, pad = 30)
    plt.tight_layout()
    plt.savefig('plots/vaccin.png')
    plt.show()

if __name__=="__main__":
    main()