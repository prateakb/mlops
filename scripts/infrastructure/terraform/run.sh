terraform init
terraform validate
terraform plan -out=tfplan
terraform apply tfplan -target=module.gke_cluster
terraform destroy
