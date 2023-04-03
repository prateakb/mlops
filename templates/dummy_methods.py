def get_data_from_source(
    use_query: str,
    path_to_csv_or_query: str,
):
    import os
    import logging
    from random import randint

    logging.basicConfig(level=logging.INFO)

    logging.info(f"Received use_query={use_query} and path_to_csv_or_query={path_to_csv_or_query}")
    # replace with dummy implementation
    df = randint(0, 100)
    return df


def preprocess(path_to_config_json: str, path_to_csv: str):
    import os
    import json
    import pandas as pd
    import logging
    import string
    import datetime
    from random import randint

    logging.basicConfig(level=logging.INFO)

    logging.info(f"Received path_to_config_json={path_to_config_json} and path_to_csv={path_to_csv}")
    # replace with dummy implementation
    df = pd.DataFrame({'A': [randint(0, 100), randint(0, 100)], 'B': [randint(0, 100), randint(0, 100)]})
    output_path = path_to_csv.replace(".csv", f"_{datetime.datetime.now().date()}_preprocessed.csv")
    df.to_csv(output_path, index=False)
    return output_path


def score(model_path: str, path_to_csv: str):
    import os
    import logging
    import xgboost as xgb
    import pandas as pd
    import datetime
    from random import randint

    logging.basicConfig(level=logging.INFO)

    logging.info(f"Received model_path={model_path} and path_to_csv={path_to_csv}")
    # replace with dummy implementation
    df = pd.DataFrame({'A': [randint(0, 100), randint(0, 100)], 'B': [randint(0, 100), randint(0, 100)], 'scores': [randint(0, 100), randint(0, 100)]})
    output_path = path_to_csv.replace(".csv", f"_{datetime.datetime.now().date()}_scored.csv")
    df.to_csv(output_path, index=False)
    logging.info(f"wrote scored data to {output_path}")
    return output_path
