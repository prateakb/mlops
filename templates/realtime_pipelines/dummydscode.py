

def preprocess(df):
    import os
    import json
    import pandas as pd
    import logging
    import string
    import datetime
    logging.basicConfig(level=logging.INFO)
    
   # clean up column names
    column_names = df.columns
    cleanup = lambda x: "".join(ch for ch in x.replace(" ", "_")  if ch in string.digits+string.ascii_letters+'_')
    cleaned_column_names = [cleanup(column) for column in column_names]
    df.columns=cleaned_column_names
    return df
    # Create first OP

def load_model():
    import xgboost as xgb
    model = xgb.Booster()
    model.load_model("model/path/to/xgboost.json")
    return model

def predict_realtime(df, model):
    import xgboost as xgb
    import json
    import pandas as pd
    import os
    import datetime

    #print(df.head())
    X = df.loc[:,[i for i in list(df.columns) ]]
    y = df.loc[:,[i for i in list(df.columns) if i in ['labels']]]
    data_matrix = xgb.DMatrix(data=X, enable_categorical = True)
    result = model.predict(data_matrix)
    return result

