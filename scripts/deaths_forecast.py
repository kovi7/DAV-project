import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_squared_error
from math import sqrt

def main():
    # Load data
    france = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', header=0, low_memory=False)

    france['date'] = pd.to_datetime(france['date'])
    france['tx_incid'] = france['tx_incid'] /100 #now it's 1 case per 100k residents

    france_deaths = france.groupby('date')['incid_dchosp'].sum().reset_index()
    france_deaths.columns = ['date', 'daily_deaths']
    # france_deaths['total_deaths'] = france_deaths['daily_deaths'].cumsum()
    france_deaths = france_deaths.set_index('date')
    daily_deaths = france_deaths['daily_deaths']

    # Check stationarity (ADF test)
    result = adfuller(daily_deaths)
    print(f"ADF statistic: {result[0]:.3f}, p-value: {result[1]:.3f}")  # data is stationary

    # # ACF and PACF plot 
    # fig, ax = plt.subplots(2,1, figsize=(10,6))
    # plot_acf(daily_deaths, lags=28, ax=ax[0])
    # plot_pacf(daily_deaths, lags=28, ax=ax[1])
    # plt.tight_layout()
    # plt.show()

    # Split the data 
    train_size = int(len(daily_deaths) - 720) # max len 1200
    train, test = daily_deaths[:train_size], daily_deaths[train_size:]

    # Model fitting
    model = SARIMAX(train, order=(1, 0, 1), seasonal_order=(1, 0, 1, 7), enforce_stationarity=True)  
    model_fit = model.fit()

    # Model forecasting with confidence intervals
    forecast_result = model_fit.get_forecast(steps=720)
    predictions = forecast_result.predicted_mean
    conf_int = forecast_result.conf_int()
    
    # Count RMSE
    rmse = sqrt(mean_squared_error(test, predictions))
    print(f'RMSE: {rmse:.2f}')

    future_dates = pd.date_range(start=daily_deaths.index[-1], periods=len(predictions)+1)[1:]

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(daily_deaths.index, daily_deaths, label='Actual', color='blue')
    plt.plot(future_dates, predictions, label='Predicted', color='red', linestyle='--')
    
    # Confidence interval shading
    lower = conf_int.iloc[:, 0]
    upper = conf_int.iloc[:, 1]
    plt.fill_between(future_dates, lower, upper, color='red', alpha=0.2, label='95% CI')

    plt.title('France Deaths Forecast', fontsize=16, weight ='bold')
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Deaths', fontsize=14)

    plt.legend()
    plt.grid(True)

    # plt.savefig('plots/deaths_forecast.png', dpi=300)
    plt.show()

if __name__=='__main__':
    main()