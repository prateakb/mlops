#!/bin/bash

# Description: Script to create a new real-time model
# Usage: ./create-realtime-model.sh

# Exit on any error
set -e

# Prompt for the name of the pipeline run
read -p "What is the name of the pipeline run? " nameofproject
# Validate the pipeline name (add specific validation logic here)
export PIPELINE_NAME="${nameofproject}"
echo "${PIPELINE_NAME}" | tr -dc '[:alnum:]\n\r' | tr ' ' '-' > PIPELINE_NAME

# Create the model directory and copy templates
mkdir -p models/${PIPELINE_NAME}/
cp -r templates/realtime_pipelines/* models/${PIPELINE_NAME}/

MAKEFILE_CONTENT="\
test:\n\
\t@echo 'checking if syntax of all python files are correct' \\\\\n\
\t\tpython -c 'import py_compile, os; [py_compile.compile(os.path.join(root, f), doraise=True) for root, dirs, files in os.walk(\".\") for f in files if f.endswith(\".py\") and not f.startswith(\"_\")]' 2>&1\n\
\n\
build:\n\
\t@echo 'there is nothing to build for a realtime model'\n\
deploy:\n\
\tbash ../../scripts/deploy-realtime.sh"

echo $(date)>VERSION
mkdir -p models/${PIPELINE_NAME}/
cp -r templates/realtime_pipelines/model models/${PIPELINE_NAME}
cp templates/realtime_pipelines/main.py models/${PIPELINE_NAME}/main.py
cp templates/realtime_pipelines/dummydscode.py models/${PIPELINE_NAME}/dummydscode.py
cp templates/realtime_pipelines/requirements.txt models/${PIPELINE_NAME}/requirements.txt
cp templates/realtime_pipelines/PIPELINE_NAME models/${PIPELINE_NAME}/PIPELINE_NAME
cp templates/realtime_pipelines/VERSION models/${PIPELINE_NAME}/VERSION
cp templates/realtime_pipelines/restructure-main.py models/${PIPELINE_NAME}/restructure-main.py

cd models/${PIPELINE_NAME}
echo "${PIPELINE_NAME}">PIPELINE_NAME
python restructure-main.py
echo "pipeline name is ${PIPELINE_NAME}"
echo "your code for a realtime model ${PIPELINE_NAME} has been configured. Please go to the folder models/${PIPELINE_NAME}"
echo "then modify the files"
echo "    - ${PIPELINE_NAME}/main.py"
echo "    - ${PIPELINE_NAME}/dummydscode.py"
echo "    - ${PIPELINE_NAME}/requirements.txt"
cd ../..

# Create the Makefile with proper formatting
echo -e ${MAKEFILE_CONTENT} > models/${PIPELINE_NAME}/Makefile
