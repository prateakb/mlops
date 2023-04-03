import sys
from kfp.registry import RegistryClient

PROJECT_ID = "your-project-id"
REGION = "your-region"  # Change this to the appropriate region if needed

yaml_file = sys.argv[1]
# Set the host URL for your KFP repository
host = f"https://{REGION}-kfp.pkg.dev/{PROJECT_ID}/your-repository-name"

# Create a RegistryClient instance
client = RegistryClient(host=host)

# Upload the pipeline to the KFP repository
template_name, version_name = client.upload_pipeline(
    file_name=yaml_file,
    tags=["v1", "latest"],
    extra_headers={"description": "This is an example pipeline template."},
)

print(f"Pipeline uploaded as {template_name}, version {version_name}")
