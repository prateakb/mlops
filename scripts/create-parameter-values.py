import json
import yaml

PARAMETER_VALUES_PATH = './schema/parameter-values.json'

# Load the compiled KFP YAML file
with open('./outputs/pipeline-build-final.yaml', 'r') as f:
    pipeline_spec = yaml.safe_load(f)

# Get the input parameters for each step
input_params = {}

# For KFP v1
if 'spec' in pipeline_spec:
    templates = pipeline_spec['spec']['templates']
    for template in templates:
        if 'inputs' in template:
            for param in template['inputs'].get('parameters', []):
                input_params[param['name']] = param['type']

# For KFP v2
elif 'pipeline_spec' in pipeline_spec:
    components = pipeline_spec['pipeline_spec']['components']
    for component in components.values():
        for param in component['input_definitions']:
            input_params[param['name']] = param['type']

# Load the previously input parameter values from the JSON file
try:
    with open(PARAMETER_VALUES_PATH, 'r') as f:
        input_values = json.load(f)
except FileNotFoundError:
    input_values = {}

# Prompt the user for input values for each parameter
for param_name, param_type in input_params.items():
    existing_value = input_values.get(param_name, '')
    value_prompt = f"Enter value for '{param_name}' ({param_type})"
    
    if existing_value:
        value_prompt += f" [Current: {existing_value}]"
    
    value_prompt += ": "
    value = input(value_prompt).strip()

    if value:
        input_values[param_name] = value
    elif not existing_value:
        input_values[param_name] = ''

# Write the updated input parameter values to the JSON file
with open(PARAMETER_VALUES_PATH, 'w') as f:
    json.dump(input_values, f)
