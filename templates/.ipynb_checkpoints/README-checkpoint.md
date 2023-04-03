

## Usage
To use this repository to register a new model, type

`make create-new-model`

This will prompt you to enter a pipeline name. The name will be sanitized by removing all non-alphanumeric characters and replacing spaces with hyphens. A new directory will be created under ./models with the sanitized name, and a prod.env file will be created in the new directory containing a single line with the original pipeline name. The environment variables defined in prod.env will be set as environment variables in the Makefile. Finally, a set of files from the templates directory (specified by the FILES_TO_COPY_TO_NEW_MODEL variable) will be copied to the new model directory.

All necessary files from the templates directory will be copied to the new model directory, and a Makefile will be generated with build, test, and pipeline run targets. The pipeline run target will use the compiled pipeline in the ./outputs directory, and will have default parameter values set.

The directory will also contain a PIPELINE_NAME file with the entered pipeline name, and a VERSION file with the current date and time stamp.

## How to Run a pipeline using parameter_values
Once you have set up a new model and modified the files appropriately, you should also compile the pipeline as a json or yaml. 

### 1.Compile your KFP pipeline using make_pipeline.py:


```
python3 make_pipeline.py
```

Create a parameter values file parameter_values.json in the following format, use it specific to your pipeline. Below sample is valid for the example make_pipeline file created where the keys are the arguments to various kfp ops.


```
{
     "use_query": "False",
     "path_to_csv_or_query": "gs://path/to/csv/or/query",
     "path_to_config_file": "gs://path/toconfig.json",
     "path_to_model": "gs://path/to/xgboost_model.json"
 }
 
 ```
### Run the pipeline using the compiled yaml and parameter-values.json

Run the pipeline using create-pipeline-run.py, passing in the path to the compiled pipeline YAML or JSON file and the path to the parameter values file:

```
python3 create-pipeline-run.py --pipeline-file /path/to/compiled/pipeline.yaml --parameter-values /path/to/parameter_values.json

```

Note: Replace the values in the example file with your actual parameter values.
