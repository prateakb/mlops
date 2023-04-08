import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyswarms as ps
import finrl
from finrl.config import config
from finrl.marketdata.yahoodownloader import YahooDownloader
from finrl.preprocessing.preprocessors import FeatureEngineer
from finrl.env.env_stocktrading import StockTradingEnv
from finrl.model.models import DRLAgent

from finrl.env.env_stocktrading import StockTradingEnv
class CustomStockTradingEnv(StockTradingEnv):
    def __init__(self, *args, **kwargs):
        self.allow_short = kwargs.pop('allow_short', False)
        super(CustomStockTradingEnv, self).__init__(*args, **kwargs)

    def _buy_stock(self, index, action):
        if index <= 0:
          return 0
        def _do_buy_normal(index):
            self.state = np.array(self.state)

            if self.state.ndim == 1:
                if (np.array(self.state[index+1], dtype=np.float64) > 0).any():
                    return self.state[index+1]/self.state[index]
            elif self.state.ndim == 2:
                if (np.array(self.state[index+1], dtype=np.float64) > 0).any():
                    return self.state[index+1]/self.state[index,0]
            return 0
        if self.turbulence_threshold is not None:
            if self.turbulence >= self.turbulence_threshold:
                # if turbulence goes over threshold, just clear out all positions 
                # irrespective of whatever signals are provided
                if index > 0:
                    if (self.state[index-1] == 0).all():
                        buy_num_shares = self.balance/self.state[index]
                        self.state[index-1] += buy_num_shares*self.state[index]
                        self.state[0] -= buy_num_shares*self.state[index]
                        return buy_num_shares
                    else:
                        return 0
                else:
                    return 0

        else:
            if index > 0:
                if (self.state[index-1] == 0):
                    buy_num_shares = _do_buy_normal(index)
                    self.state[index-1] += buy_num_shares*self.state[index]
                    self.state[0] -= buy_num_shares*self.state[index]
                    return buy_num_shares
                else:
                    return 0
            else:
                return 0



    def _sell_stock(self, index, action):
        if index <= 0:
          return 0
        
        def _do_sell_normal(index):
            self.state = np.array(self.state)
            if self.state.ndim == 1:
                if (index+1 < len(self.state)) and (np.array(self.state[index+1], dtype=np.float64) > 0).any():
                    return self.state[index+1]/self.state[index]
            elif self.state.ndim == 2:
                if (index+1 < len(self.state)) and (np.array(self.state[index+1], dtype=np.float64) > 0).any():
                    return self.state[index+1]/self.state[index,0]
            return 0

        if self.turbulence_threshold is not None:
            if self.turbulence >= self.turbulence_threshold:
                  # if turbulence goes over threshold, just clear out all positions 
                  # irrespective of whatever signals are provided
                  if index > 0:
                      if (self.state[index-1] == 0).all():
                          return 0
                      else:
                          sell_num_shares = self.state[index-1]//self.state[index]
                          self.state[index-1] -= sell_num_shares*self.state[index]
                          self.state[index] += sell_num_shares*self.state[index]
                          return sell_num_shares            
                  else:
                      return 0

        else:
              if index > 0:
                      sell_num_shares = _do_sell_normal(index)
                      self.state[index-1] -= sell_num_shares*self.state[index]
                      self.state[index] += sell_num_shares*self.state[index]
                      return sell_num_shares
              else:
                  return 0



def apply_pso_weights(env, weights):
    state = env.reset()
    done = False
    while not done:
        raw_action = np.array([np.dot(state, w) for w in weights.reshape(-1, len(state))])
        raw_action_min, raw_action_max = raw_action.min(), raw_action.max()
        action = (raw_action - raw_action_min) / (raw_action_max - raw_action_min)  # Normalize the action between 0 and 1

        action = env.action_space.low + action * (env.action_space.high - env.action_space.low)  # Scale the action to the bounds of the action_space
        state, reward, done, _ = env.step(action)

    trade_results = env.save_asset_memory()
    return trade_results



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

print("train_data's shape: ", train_data.shape)

stock_dimension = len(config.TICKER_LIST)
state_space = 1 + 2 * stock_dimension + len(config.TECHNICAL_INDICATORS_LIST) * stock_dimension
env_kwargs = {
    "hmax": 20,
    "initial_amount": 20000,
    "buy_cost_pct": 0.001,
    "sell_cost_pct": 0.001,
    "state_space": state_space,
    "stock_dim": stock_dimension,
    "tech_indicator_list": config.TECHNICAL_INDICATORS_LIST,
    "action_space": stock_dimension,
    "reward_scaling": 1e-2,
    "allow_short": False
}

def fitness_function(weights, env_kwargs):
    env_train = CustomStockTradingEnv(df=train_data, **env_kwargs)
    state = env_train.reset()
    done = False
    while not done:
        print(f"state length: {len(state)}")  # Print state length
        print(f"weights shape: {weights.shape}")  # Print weights shape
        raw_action = np.array([np.dot(state, w) for w in weights.reshape(-1, len(state))])
        print(f"raw_action: {raw_action}")  # Print raw_action
        raw_action_min, raw_action_max = raw_action.min(), raw_action.max()
        action = (raw_action - raw_action_min) / (raw_action_max - raw_action_min)  # Normalize the action between 0 and 1

        action = env_train.action_space.low + action * (env_train.action_space.high - env_train.action_space.low)  # Scale the action to the bounds of the action_space
        state, reward, done, _ = env_train.step(action)
        print(f"state after step: {state}")  # Print state after step

    terminal_data = env_train.save_asset_memory()
    total_profit = terminal_data['account_value'].iloc[-1] - env_kwargs.get("initial_amount")

    return -total_profit








# Set up the PSO algorithm by specifying the number of particles, the dimensions, and other parameters
num_particles = 50
dimensions = env_kwargs["state_space"] * env_kwargs["action_space"]

bounds = (np.zeros(dimensions), np.ones(dimensions) * 20)  # Set bounds for the weights

options = {"c1": 0.5, "c2": 0.3, "w": 0.9}
optimizer = ps.single.GlobalBestPSO(
    n_particles=num_particles,
    dimensions=dimensions,
    options=options,
    bounds=bounds
)
# Run the PSO algorithm to find the optimal weights
cost, best_weights = optimizer.optimize(lambda x: fitness_function(x, env_kwargs), iters=1000)

# Define the environment for the trade data
env_trade = CustomStockTradingEnv(df=trade_data, **env_kwargs)

# Get the trade results using the best_weights found by PSO
pso_trade_results = apply_pso_weights(env_trade, best_weights)

print(pso_trade_results)

# Calculate the total profit
initial_amount = env_kwargs.get("initial_amount")
final_amount = pso_trade_results.iloc[-1]['account_value']
total_profit = final_amount - initial_amount

# Calculate the drawdown
pso_trade_results['max_value'] = pso_trade_results['account_value'].cummax()
pso_trade_results['drawdown'] = pso_trade_results['max_value'] - pso_trade_results['account_value']
max_drawdown = pso_trade_results['drawdown'].max()

print(f"Total Profit: {total_profit:.2f}")
print(f"Max Drawdown: {max_drawdown:.2f}")