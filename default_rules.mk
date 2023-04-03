.DEFAULT_GOAL := create-new-model
# Set default values for the pipeline file and parameter values
PIPELINE_FILE = outputs/pipeline-build-final.yaml
PARAMETER_VALUES = schema/parameter-values.json

test:
	@echo "no test on main folder"

build:
	@echo "no build on main folder"

deploy:
	@echo "no deploy on main folder"

create-new-model:
	@read -p "Is this a new model for real-time consumption? [y/N]: " realtime; \
	if [ "$$realtime" = "y" ] || [ "$$realtime" = "Y" ]; then \
		echo "Creating a new real-time model..."; \
		bash ./scripts/create-realtime-model.sh; \
	else \
		echo "Creating a new batch model..."; \
		bash ./scripts/create-batch-model.sh; \
	fi

clean-pycache:
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete
