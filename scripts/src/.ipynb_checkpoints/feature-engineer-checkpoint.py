import glob
import pandas as pd
import re
import yfinance as yf

def remove_correlated_features(final_data, target_column, threshold=0.8):
    # Calculate the correlation matrix
    corr_matrix = final_data.corr()

    # Identify highly correlated features
    correlated_features = set()
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                colname = corr_matrix.columns[i]
                if colname != target_column:
                    correlated_features.add(colname)
    print("the correlated features are \n", correlated_features) 
    # Remove highly correlated features
    final_data.drop(columns=correlated_features, inplace=True)
    return final_data

def download_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    stock_data.reset_index(inplace=True)
    stock_data.rename(columns={'Date': 'date', 'Close': 'stock_price'}, inplace=True)
    return stock_data

def sanitize_series_name(series_name):
    return re.sub(r'\W+', '_', series_name)

def read_and_merge_parquet_files():
    parquet_files = glob.glob('../*.parquet')

    merged_data = pd.DataFrame()

    for file in parquet_files:
        # Check if the series is not discontinued
        if "DISCONTINUED" not in file:
            data = pd.read_parquet(file)
            
            # Sanitize the series name
            series_name = sanitize_series_name(data['series'].iloc[0])
            data.drop(columns=['release', 'series'], inplace=True)
            data.rename(columns={'value': series_name}, inplace=True)

            if merged_data.empty:
                merged_data = data
            else:
                merged_data = pd.merge(merged_data, data, on='date', how='outer')

    return merged_data

def read_stock_ticker_data(stock_data_path):
    stock_data = pd.read_csv(stock_data_path)
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    return stock_data

def merge_data(merged_data, stock_data):
    final_data = pd.merge(merged_data, stock_data, on='date', how='outer')
    return final_data

def fill_missing_values(final_data, method='ffill'):
    final_data.fillna(method=method, inplace=True)
    return final_data

def shift_features(final_data, feature_columns, shift_period=1):
    final_data[feature_columns] = final_data[feature_columns].shift(shift_period)
    final_data.dropna(inplace=True)
    return final_data

if __name__ == "__main__":
    # Read and merge parquet files
    merged_data = read_and_merge_parquet_files()

    # Download stock ticker price data
    ticker = 'AAPL'
    start_date = '1980-01-01'
    end_date = '2022-12-31'
    stock_data = download_stock_data(ticker, start_date, end_date)


    # Merge stock ticker price data with merged_data
    final_data = merged_data

    # Fill missing values
    final_data = fill_missing_values(final_data, method='ffill')

    # Define the feature columns
    feature_columns = list(final_data.columns)

    # Remove correlated features
    correlation_threshold = 0.8
    final_data = remove_correlated_features(final_data, 'stock_price', threshold=correlation_threshold)

    # Save the final DataFrame to a CSV file
    final_data.to_csv("final_data.csv", index=False)
