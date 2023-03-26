resource "aws_eks_cluster" "eks_cluster" {
  name     = var.cluster_name
  role_arn = var.role_arn

  vpc_config {
    subnet_ids = var.subnet_ids
  }
}

locals {
  cluster_security_group_id = aws_eks_cluster.eks_cluster.vpc_config[0].cluster_security_group_id
}

resource "aws_security_group" "worker_group_mgmt_one" {
  name_prefix = "worker_group_mgmt_one"
  description = "EKS worker group management one"
  vpc_id      = var.vpc_id
}

resource "aws_security_group" "worker_group_mgmt_two" {
  name_prefix = "worker_group_mgmt_two"
  description = "EKS worker group management two"
  vpc_id      = var.vpc_id
}

module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name = var.cluster_name
  subnets      = var.subnet_ids

  tags = {
    Terraform = "true"
    Cluster   = var.cluster_name
  }

  vpc_id = var.vpc_id

  node_groups_defaults = {
    ami_type  = "AL2_x86_64"
    disk_size = 20
  }

  node_groups = {
    eks_nodes = {
      desired_capacity = var.min_nodes
      max_capacity     = var.max_nodes
      min_capacity     = var.min_nodes

      instance_type = var.instance_type
      additional_tags = {
        Terraform = "true"
        Cluster   = var.cluster_name
      }
    }
  }

  manage_aws_auth = true

  write_kubeconfig      = false
  config_output_path    = "./kubeconfig_${var.cluster_name}"
  write_aws_auth_config = false
  aws_auth_config_output_path = "./aws_auth_${var.cluster_name}.yaml"
}
