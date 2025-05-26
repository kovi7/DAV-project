import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_squared_error
from math import sqrt

def main():
    # Load data
    data = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', usecols = ['date','lib_reg','TO','hosp','rea', 'rad','dchosp','reg_rea'])
    data['date'] = pd.to_datetime(data['date'])

    data['year'] = data['date'].dt.year

    # Log-transformation
    series = data.groupby('date')['hosp'].sum()

    # Per capita normalization 
    FRANCE_POPULATION = 67_000_000  # Approximate population of France 
    SCALING_FACTOR = 100_000  

    # Compute hospitalizations per 100k
    series_per_capita = (series / FRANCE_POPULATION) * SCALING_FACTOR

    # Check stationarity (ADF test)
    result = adfuller(series_per_capita)
    print(f"ADF statistic: {result[0]:.3f}, p-value: {result[1]:.3f}")  # data is stationary

    # # ACF and PACF plot 
    # fig, ax = plt.subplots(2,1, figsize=(10,6))
    # plot_acf(series, lags=28, ax=ax[0])
    # plot_pacf(series, lags=28, ax=ax[1])
    # plt.tight_layout()
    # plt.show()

    # Split the data 
    train_size = int(len(series_per_capita) - 720) # max len = 1200
    train, test = series_per_capita[:train_size], series_per_capita[train_size:]

    # Model fitting
    model = SARIMAX(train, order=(1, 0, 2), seasonal_order=(1, 0, 1, 7), enforce_stationarity=True)  
    model_fit = model.fit()

    # Model forecasting with confidence intervals
    forecast_result = model_fit.get_forecast(steps=720)
    predictions = forecast_result.predicted_mean
    conf_int = forecast_result.conf_int()
    
    # Count RMSE
    rmse = sqrt(mean_squared_error(test, predictions))
    print(f'RMSE: {rmse:.2f}')

    future_dates = pd.date_range(start=series_per_capita.index[-1], periods=len(predictions)+1)[1:]

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(series_per_capita.index, series_per_capita, label='Actual', color='blue')
    plt.plot(future_dates, predictions, label='Predicted', color='red', linestyle='--')
    
    # Confidence interval shading
    lower = conf_int.iloc[:, 0]
    upper = conf_int.iloc[:, 1]
    plt.fill_between(future_dates, lower, upper, color='red', alpha=0.2, label='95% CI')

    plt.title('France Hospitalizations Forecast', fontsize=16, weight ='bold')
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Hospitalizations (per 100k people)', fontsize=14)

    plt.legend()
    plt.grid(True)

    plt.savefig('plots/daily_hosp_forecast.png', dpi=300)
    plt.show()

if __name__=='__main__':
    main()