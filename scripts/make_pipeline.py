import os
import string
import json
import sys
import argparse
from datetime import date
import kfp.v2 as kfp
from kfp.v2 import compiler
from kfp.v2.dsl import (
    component as comp,
    InputPath,
    Input,
    Output,
    OutputPath,
    
)
from dummy_methods import get_data, preprocess, score
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "your-project-name")
include_chars = string.ascii_letters + string.digits
PIPELINE_ID = "".join([ch for ch in PIPELINE_NAME if ch in include_chars])
BASE_IMAGE = f"gcr.io/your_project_id/base-image-{PIPELINE_NAME}:latest"
JSON_FILE_NAME = f"{PIPELINE_NAME}_{date.today()}.json"
YAML_FILE_NAME = f"{PIPELINE_NAME}_{date.today()}.yaml"

# Create pipeline components
@comp(base_image=BASE_IMAGE)
def get_data_op(
    use_query: str, path_to_csv_or_query: str
) -> str:
    # Replace this with your implementation
    from dummy_methods import get_data
    return "get_data_op"


@comp(base_image=BASE_IMAGE)
def preprocess_op(
    path_to_config_file: str, path_to_csv: str
) -> str:
    # Replace this with your implementation
    from dummy_methods import preprocess
    return "preprocess_op"


@comp(base_image=BASE_IMAGE)
def score_op(
    path_to_model: str, path_to_csv: str
) -> str:
    # Replace this with your implementation
    from dummy_methods import score
    return "score_op"


# Define the pipeline
@kfp.dsl.pipeline(
    name=PIPELINE_ID,
    description=f"This pipeline scores the {PIPELINE_NAME} model using Vertex AI Pipelines",
)
def score_pipeline(
    use_query: str= "False",
    path_to_csv_or_query: str = "gs://your_bucket_name/input_csv.csv",
    path_to_config_file: str = "gs://your_bucket_name/input_csv.csv",
    path_to_model: str = "gs://your_bucket_name/xgboost_model.json",
):

    task_1 = get_data_op(use_query, path_to_csv_or_query)
    task_2 = preprocess_op(path_to_config_file, path_to_csv_or_query)
    task_3 = score_op(path_to_model, path_to_csv_or_query)

    task_3.after(task_2)
    task_2.after(task_1)

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--from-build", action="store_true", help="Save output file as pipeline-build-final.yaml")
args = parser.parse_args()

if args.from_build:
    YAML_FILE_NAME = "pipeline-build-final.yaml"

# Compile and save the pipeline as JSON
temp_json_file_path = f"./outputs/temp_{JSON_FILE_NAME}"
compiler.Compiler().compile(pipeline_func=score_pipeline, package_path=temp_json_file_path)

# Read the JSON file and convert it to YAML
with open(temp_json_file_path, 'r') as json_file:
    pipeline_json = json.load(json_file)

pipeline_yaml = yaml.safe_dump(pipeline_json)

# Save the YAML file
with open(f"./outputs/{YAML_FILE_NAME}", 'w') as yaml_file:
    yaml_file.write(pipeline_yaml)
# Remove the temporary JSON file
os.remove(temp_json_file_path)
