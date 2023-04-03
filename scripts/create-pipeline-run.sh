import argparse
import json
import yaml
import os
from datetime import date
from google.cloud import aiplatform

# Set the project and staging bucket names
PROJECT_ID = "your_project_id"
STAGING_BUCKET_NAME = "your_staging_bucket_name"

# Read the pipeline name from the PIPELINE_NAME file
with open("PIPELINE_NAME", "r") as f:
    PIPELINE_NAME = f.read().strip()

# Initialize the AI Platform client
aiplatform.init(
    project=PROJECT_ID,
    location='your_location',
    staging_bucket=STAGING_BUCKET_NAME
)

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--pipeline-file", type=str, required=True, help="Path to KFP compiled pipeline YAML or JSON file")
parser.add_argument("--parameter-values", type=str, required=True, help="Path to JSON or YAML file containing pipeline parameter values")
args = parser.parse_args()

# Load the pipeline parameter values from the parameter values JSON
with open(args.parameter_values) as f:
    parameter_values = json.loads(f.read()) if args.parameter_values.endswith('.json') else yaml.safe_load(f.read())

# Submit the pipeline job to Vertex AI Pipelines
pipeline = aiplatform.PipelineJob(
    display_name=f"{PIPELINE_NAME}-{date.today()}",
    pipeline_root="gs://{}/vertex-staging".format(STAGING_BUCKET_NAME),
    template_path=args.pipeline_file,
    parameter_values=parameter_values,
    enable_caching=False
)

try:
    pipeline.run(sync=True)
    print(f"Pipeline job for {args.pipeline_file} submitted successfully.")
except Exception as e:
    print(f"Error running Pipeline job for {args.pipeline_file}\n{e}")
