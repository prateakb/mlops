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

# Define the problem: What is the goal of the trading strategy? What are the decision variables?
# Here, we want to maximize the total return while minimizing the risk.
# The decision variables are the weights for each stock and the weight for the macroeconomic indicator.
def fitness_function(weights, data):

    portfolio_returns = data.groupby('tic')['close'].pct_change(1)


    # Calculate the mean and standard deviation of the portfolio returns
    mean_return = np.mean(portfolio_returns)
    std_return = np.std(portfolio_returns)
    
    # Calculate the Sharpe ratio of the portfolio
    sharpe_ratio = mean_return / std_return
    
    # Return the negative Sharpe ratio to maximize the Sharpe ratio
    return -sharpe_ratio
# Define the genetic algorithm parameters
POPULATION_SIZE = 100
NUM_GENERATIONS = 50
MUTATION_RATE = 0.1

# Define the decision variable bounds
# The bounds for the stock weights are [0, 1], and the bounds for the macro weight are [-1, 1].
bounds = [(0, 1)] * (len(train_data.columns) - 1)
bounds.append((-1, 1))

# Define the initial population
population = np.random.uniform(size=(POPULATION_SIZE, len(bounds)))
population = np.clip(population, 0, 1)
population[:, -1] = np.random.uniform(-1, 1, size=POPULATION_SIZE)

# Iterate through the generations
for generation in range(NUM_GENERATIONS):
    # Evaluate the fitness of the population
    fitness_values = [fitness_function(weights, train_data) for weights in population]
    fitness_values = np.array(fitness_values)
    probabilities = fitness_values / np.sum(fitness_values)
    parent_indices = np.random.choice(
        POPULATION_SIZE,
        size=POPULATION_SIZE,
        replace=True,
        p=probabilities
    )

    # Create the offspring by crossover and mutation
    offspring = np.zeros_like(population)
    for i in range(POPULATION_SIZE):
        parent1_index = parent_indices[i]
        parent2_index = parent_indices[np.random.randint(POPULATION_SIZE)]
        crossover_point = np.random.randint(len(bounds))
        offspring[i, :crossover_point] = population[parent1_index, :crossover_point]
        offspring[i, crossover_point:] = population[parent2_index, crossover_point:]
        if np.random.rand() < MUTATION_RATE:
            offspring[i] = np.clip(offspring[i] + np.random.normal(size=len(bounds)), 0, 1)
            offspring[i, -1] = np.clip(offspring[i, -1] + np.random.normal(scale=0.1), -1, 1)
    
    # Replace the old population with the offspring
    population = offspring
    
    # Print the best fitness value in this generation
    best_fitness = np.min(fitness_values)
    print(f"Generation {generation+1}, Best Fitness: {best_fitness:.2f}")
    
# Obtain the optimal weights from the best individual in the final population
best_index = np.argmin(fitness_values)
optimal_weights = population[best_index]
optimal_weights = np.clip(optimal_weights, 0, 1)
optimal_weights[-1] = np.clip(optimal_weights[-1], -1, 1)

# Split the optimal weights into stock weights and macroeconomic weight
stock_weights = optimal_weights

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

# Define the environment for the trade data
env_trade = StockTradingEnv(df=trade_data, **env_kwargs)

# Use the optimal weights to predict actions for the trade data
actions = []
trade_data.reset_index(drop=True, inplace=True)
for i in range(len(trade_data)):
    action = [0] * stock_dimension
    for j, ticker in enumerate(config.TICKER_LIST):
        action[j] = stock_weights[j]
    actions.append(action)
actions = pd.DataFrame(actions, index=trade_data.index)

# Run the trading simulation using the predicted actions
results = env_trade.step(actions)

# Calculate profits and drawdowns
account_values = results['account_value']
initial_amount = env_kwargs.get("initial_amount")
final_amount = account_values.iloc[-1]
total_profit = final_amount - initial_amount

account_values['max_value'] = account_values['account_value'].cummax()
account_values['drawdown'] = account_values['max_value'] - account_values['account_value']
max_drawdown = account_values['drawdown'].max()

print(f"Total Profit: {total_profit:.2f}")
print(f"Max Drawdown: {max_drawdown:.2f}")
