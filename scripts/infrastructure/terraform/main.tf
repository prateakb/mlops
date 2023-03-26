# Configure the Google Cloud provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Configure the AWS provider
provider "aws" {
  region = var.aws_region
}

module "gke_cluster" {
  source = "./modules/gke"

  project_id = var.project_id
  region     = var.region
  vpc_name   = var.vpc_name
  subnet_name = var.subnet_name
  cluster_name = var.cluster_name
  min_nodes    = var.min_nodes
  max_nodes    = var.max_nodes
  machine_type = var.machine_type
}

module "eks_cluster" {
  source = "./modules/eks"

  aws_region     = var.aws_region
  cluster_name   = var.cluster_name
  vpc_id         = var.vpc_id
  subnet_ids     = var.subnet_ids
  min_nodes      = var.min_nodes
  max_nodes      = var.max_nodes
  instance_type  = var.instance_type
  key_name       = var.key_name
  role_arn       = var.role_arn
}
