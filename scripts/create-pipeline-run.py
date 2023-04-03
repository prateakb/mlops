import os
import re
import string
import time
import argparse
import json
import yaml
from datetime import date

from google.cloud import storage
from google.cloud import aiplatform
import kfp
from kfp.v2 import compiler
from kfp.v2.google.client import AIPlatformClient

# Set the project and staging bucket names
PROJECT_ID = "your_project_id"
STAGING_BUCKET_NAME = "your_staging_bucket_name"

# Initialize the AI Platform client
aiplatform.init(
    project=PROJECT_ID,
    location='your_location',
    staging_bucket=STAGING_BUCKET_NAME
)
aiplatform_client = aiplatform

# Initialize the Cloud Storage client
storage_client = storage.Client(project=PROJECT_ID)

# Define the pipeline name and ID
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "your_project_name")
include_chars = string.ascii_letters + string.digits
PIPELINE_ID = "".join([ch for ch in PIPELINE_NAME if ch in include_chars])

# Define the base image for the pipeline
BASE_IMAGE = f"gcr.io/{PROJECT_ID}/base-image-{PIPELINE_NAME}:latest"

parser = argparse.ArgumentParser()
parser.add_argument("--pipeline-file", type=str, default="outputs/pipeline-build-final.yaml", help="Path to KFP compiled pipeline YAML or JSON file")
parser.add_argument("--parameter-values", type=str, default="schema/parameter-values.json", help="Path to JSON or YAML file containing pipeline parameter values")
args = parser.parse_args()

# Load the pipeline parameter values from the parameter values JSON or YAML file
with open(args.parameter_values) as f:
    parameter_values =json.loads(f.read())

# Submit the pipeline job to Vertex AI Pipelines
pipeline = aiplatform.PipelineJob(
    display_name=f"{PIPELINE_NAME}-{date.today()}",
    pipeline_root="gs://your_bucket_name/vertex-staging",
    template_path=args.pipeline_file,
    parameter_values=parameter_values,
    enable_caching=False
)

try:
    pipeline.run(sync=True)
    print(f"Pipeline job for {args.pipeline_file} submitted successfully.")
except Exception as e:
    print(f"Error running Pipeline job for {args.pipeline_file} \n {e}")
