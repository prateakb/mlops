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
config.TICKER_LIST = ['EURUSD=X']

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
    "hmax": 100,
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
# Train multiple models
models = [ "a2c", "sac"]#, "ddpg", "ppo"]
trained_models = {}
agent = DRLAgent(env=env_train)
for model_name in models:
    model = agent.get_model(model_name)
    trained_model = agent.train_model(model=model, tb_log_name=model_name, total_timesteps=20_000)
    trained_models[model_name] = trained_model

# Use the trained models to predict actions for the trade data
# Use the trained models to predict actions for the trade data
results = []
obs = env_trade.reset()
done = False
while not done:
    action_dict = get_actions(obs, trained_models)
    obs, reward, done, info = env_trade.step(action_dict)
    results.append(action_dict)

# Average the predictions made by all the models
ensemble_predictions = np.mean(np.array(results), axis=0)

# Reset the index and add the 'day' column to the trade data
trade_data = trade_data.reset_index(drop=True)
trade_data.reset_index(inplace=True)
trade_data['day'] = trade_data.index
trade_data.set_index(['date', 'tic'], inplace=True)
trade_data.reset_index(inplace=True)

# Use the ensembled predictions to simulate trading on the trade data
env_trade = StockTradingEnv(df=trade_data, **env_kwargs)
actions = []
account_values = []
profits = []
drawdowns = []
obs = env_trade.reset()
done = False
while not done:
    action_dict = {tic: ensemble_predictions[i] for i, tic in enumerate(config.TICKER_LIST)}
    actions.append(action_dict)
    obs, reward, done, info = env_trade.step(action_dict)
    account_values.append(info['account_value'])
    profits.append(info['total_profit'])
    drawdowns.append(info['max_drawdown'])

# Create a dataframe with the simulation results
results = pd.DataFrame({
    'actions': actions,
    'account_value': account_values,
    'profit': profits,
    'drawdown': drawdowns
})

# Plot the account value, profits, and drawdowns over time
fig, axs = plt.subplots(3, 1, figsize=(10, 10))
results['account_value'].plot(ax=axs[0])
axs[0].set_title('Account Value')
results['profit'].plot(ax=axs[1])
axs[1].set_title('Profit')
results['drawdown'].plot(ax=axs[2])
axs[2].set_title('Drawdown')
plt.show()

# Visualize the actions taken by the models over time
for day in range(len(results)):
    actions = results.loc[day, 'actions']
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (tic, action) in enumerate(actions.items()):
        color = 'g' if action > 0 else 'r'
        ax.bar(i, abs(action), color=color)
        ax.set_xticks(range(len(actions)))
        ax.set_xticklabels(list(actions.keys()))
    plt.title(f'Day {day}')
    plt.show()
