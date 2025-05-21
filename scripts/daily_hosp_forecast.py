import pandas as pd
import numpy as np
import plotly.graph_objects as go
import calendar
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_squared_error
from math import sqrt


# Load data
data = pd.read_csv('data/table-indicateurs-open-data-dep-2023-06-30-17h59.csv', usecols = ['date','lib_reg','TO','hosp','rea', 'rad','dchosp','reg_rea'])
data['date'] = pd.to_datetime(data['date'])

data['day_of_year'] = data['date'].dt.day_of_year
data['month_name'] = data['date'].dt.strftime('%B')
data['month_num'] = data['date'].dt.month
data['year'] = data['date'].dt.year

# Group by year, month, and day
data_by_day_month = data.groupby(['year', 'day_of_year','month_num', 'month_name'])['hosp'].sum().reset_index()

# Log-transformacja dla stabilnej wariancji
series = np.log1p(data.groupby('date')['hosp'].sum())

# Check stationarity (ADF test)
result = adfuller(series)
print(f"ADF statistic: {result[0]:.3f}, p-value: {result[1]:.3f}")  # data is stationary

# # ACF and PACF plot 
# fig, ax = plt.subplots(2,1, figsize=(10,6))
# plot_acf(series, lags=30, ax=ax[0])
# plot_pacf(series, lags=30, ax=ax[1])
# plt.tight_layout()
# plt.show()

# Split the data 
train_size = int(len(series) - 700)
train, test = series[:train_size], series[train_size:]

# Model fitting
model = ARIMA(train, order=(2, 0, 2))  #  p, d, q parameters
model_fit = model.fit()

 # Model forecasting
predictions = model_fit.forecast(steps=700)

# Count RMSE
rmse = sqrt(mean_squared_error(test, predictions))
print(f'RMSE: {rmse:.2f}')

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(series.index, series, label='Actual', color='blue')
    
future_dates = pd.date_range(start=series.index[-1], periods=len(predictions)+1)[1:]

plt.plot(future_dates, predictions, label='Predicted', color='red', linestyle='--')
    
plt.title('Hospitalizations Prediction with ARIMA', fontsize=16)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Hospitalizations', fontsize=14)
plt.legend()
plt.grid(True)
plt.show()