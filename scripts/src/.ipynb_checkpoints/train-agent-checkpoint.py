import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import finrl
from finrl.config import config
from finrl.marketdata.yahoodownloader import YahooDownloader
from finrl.preprocessing.preprocessors import FeatureEngineer
from finrl.env.env_stocktrading import StockTradingEnv
from finrl.model.models import DRLAgent

# Define the date range and stock tickers in the config
config.START_DATE = "2010-01-01"
config.END_DATE = "2021-09-30"
config.TICKER_LIST = ['SPY']

# Load the final_data CSV file
final_data = pd.read_csv("final_data.csv")

# Convert the 'date' column of both price_data and final_data to datetime format
price_data = YahooDownloader(start_date=config.START_DATE,
                             end_date=config.END_DATE,
                             ticker_list=config.TICKER_LIST).fetch_data()
price_data['date'] = pd.to_datetime(price_data['date'])
final_data['date'] = pd.to_datetime(final_data['date'])

# Merge the price_data and final_data on the 'date' column, and fill missing values using forward fill
merged_data = pd.merge(final_data, price_data, on='date', how='inner')
merged_data.fillna(method='ffill', inplace=True)
#merged_data = merged_data[~merged_data.index.duplicated(keep='first')]

# Calculate the daily returns
merged_data['daily_return'] = merged_data.groupby('tic')['close'].pct_change(1)

# Perform feature engineering on the merged data
fe = FeatureEngineer(
    use_technical_indicator=True,
    use_turbulence=False,
    user_defined_feature=True
)
processed_data = fe.preprocess_data(merged_data)

# Split the processed data into training and trading data
train_data = processed_data[(processed_data.date < '2021-01-01')]
trade_data = processed_data[(processed_data.date >= '2021-01-01')]

# Reset the index and add the 'day' column to the training data
train_data = train_data.reset_index(drop=True)
train_data.reset_index(inplace=True)
train_data['day'] = train_data.index
train_data.set_index(['date', 'tic'], inplace=True)
train_data.reset_index(inplace=True)

trade_data = trade_data.reset_index(drop=True)
trade_data.reset_index(inplace=True)
trade_data['day'] = trade_data.index
trade_data.set_index(['date', 'tic'], inplace=True)
trade_data.reset_index(inplace=True)

print(train_data.shape, trade_data.shape)

# Define the environment for reinforcement learning
stock_dimension = len(config.TICKER_LIST)
state_space = 1 + 2 * stock_dimension + len(config.TECHNICAL_INDICATORS_LIST) * stock_dimension
env_kwargs = {
    "hmax": 6,
    "initial_amount": 20000,
    "buy_cost_pct": 0.001,
    "sell_cost_pct": 0.001,
    "state_space": state_space,
    "stock_dim": stock_dimension,
    "tech_indicator_list": config.TECHNICAL_INDICATORS_LIST,
    "action_space": stock_dimension,
    "reward_scaling": 1e-2
}
env_train = StockTradingEnv(df=train_data, **env_kwargs)

# Create the reinforcement learning model (DDPG in this case) and train it
agent = DRLAgent(env=env_train)
DDPG_PARAMS = {
    "buffer_size": 20_000,
    "learning_rate": 0.005,
    "batch_size": 64
}
model_ddpg = agent.get_model("ddpg", model_kwargs=DDPG_PARAMS)
trained_ddpg = agent.train_model(model=model_ddpg, tb_log_name='ddpg', total_timesteps=20_000)
# Reset the index and add the 'day' column to the trade data
trade_data = trade_data.reset_index(drop=True)
trade_data.reset_index(inplace=True)
trade_data['day'] = trade_data.index
trade_data.set_index(['date', 'tic'], inplace=True)
trade_data.reset_index(inplace=True)

# Define the environment for the trade data
env_trade = StockTradingEnv(df=trade_data, **env_kwargs)

# Use the trained model to predict actions for the trade data
trade_results = agent.DRL_prediction(model=trained_ddpg, environment=env_trade)

# Calculate profits and drawdowns


print(trade_results)
#trade_results.to_csv("trade_results.csv", index = False)


# Unpack the trade_data tuple
account_values, actions = trade_results

# Calculate the total profit
initial_amount = env_kwargs.get("initial_amount")
final_amount = account_values.iloc[-1]['account_value']
total_profit = final_amount - initial_amount

# Calculate the drawdown
account_values['max_value'] = account_values['account_value'].cummax()
account_values['drawdown'] = account_values['max_value'] - account_values['account_value']
max_drawdown = account_values['drawdown'].max()

print(f"Total Profit: {total_profit:.2f}")
print(f"Max Drawdown: {max_drawdown:.2f}")