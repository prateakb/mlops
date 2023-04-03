#!/bin/bash
set -e
FILES_TO_COPY_TO_NEW_MODEL=(
    "templates/Dockerfile"
    "templates/README.md"
    "templates/VERSION"
    "templates/dummy_methods.py"
    "scripts/make_pipeline.py"
    "scripts/make_pipeline.sh"
    "templates/requirements.txt"
    "scripts/create-pipeline-run.py"
    "templates/schema/"
    "templates/outputs"
)

cat > makefile_temp << EOM

PIPELINE_FILE = outputs/pipeline-build-final.yaml
PARAMETER_VALUES = schema/parameter-values.json

build:
    @echo 'Finding pipeline name...'
    @sanitized_name=\$\$(cat ./prod.env | grep PIPELINE_NAME | cut -d'=' -f2 | tr ' ' '-'); \\
    echo 'Pipeline name found: \$\$sanitized_name'; \\
    echo 'Running make_pipeline.sh...'; \\
    bash make_pipeline.sh; \\
    echo 'make_pipeline.sh completed successfully. Please find your compiled yaml at ./outputs/pipeline-final-build.yaml folder'

create-pipeline-run:
    python3 create-pipeline-run.py \\
        --pipeline-file \$(PIPELINE_FILE) \\
        --parameter-values \$(PARAMETER_VALUES)

make-run-pipeline:
    make create-pipeline-run PIPELINE_FILE=\$(PIPELINE_FILE) PARAMETER_VALUES=\$(PARAMETER_VALUES)

run-pipeline:
    @if [ -z "\$(pipeline_file)" ]; then \\
        read -p "Enter pipeline file path: " pipeline_file; \\
    fi; \\
    if [ -z "\$(parameter_values)" ]; then \\
        read -p "Enter parameter values path: " parameter_values; \\
    fi; \\
    make create-pipeline-run PIPELINE_FILE=\$\$pipeline_file PARAMETER_VALUES=\$\$parameter_values

test:
    @echo 'checking if syntax of all python files are correct' \\
    python -c 'import py_compile, os; [py_compile.compile(os.path.join(root, f), doraise=True) for root, dirs, files in os.walk(".") for f in files if f.endswith(".py") and not f.startswith("_")]' 2>&1

deploy:
    bash ../../scripts/deploy.sh
EOM

sed 's/^    /\t/' makefile_temp > ./scripts/Makefile
rm makefile_temp

read -p 'Enter pipeline name: ' pipeline_name
sanitized_name=$(echo "$pipeline_name" | tr -dc '[:alnum:]\n\r' | tr ' ' '-')
mkdir -p ./models/"$sanitized_name"
echo "Writing to ./models/$sanitized_name/prod.env"
echo "PIPELINE_NAME=$pipeline_name" > ./models/"$sanitized_name"/prod.env
export $(cat ./models/"$sanitized_name"/prod.env | xargs)
echo "Environment variables initialized from prod.env"
cp -r "${FILES_TO_COPY_TO_NEW_MODEL[@]}" ./models/"$sanitized_name"
cp ./scripts/Makefile ./models/"$sanitized_name"/Makefile
echo "$pipeline_name" > ./models/"$sanitized_name"/PIPELINE_NAME
date '+%Y-%m-%d %H:%M:%S' > ./models/"$sanitized_name"/VERSION