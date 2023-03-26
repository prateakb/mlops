resource "google_container_cluster" "gke_cluster" {
  name     = var.cluster_name
  location = var.region
  project  = var.project_id

  network    = var.vpc_name
  subnetwork = var.subnet_name

  initial_node_count = var.min_nodes

  node_config {
    machine_type = var.machine_type
  }

  node_pool {
    name       = "default-pool"
    node_count = var.min_nodes

    autoscaling {
      min_node_count = var.min_nodes
      max_node_count = var.max_nodes
    }

    management {
      auto_repair  = true
      auto_upgrade = true
    }
  }

  timeouts {
    create = "30m"
    delete = "30m"
  }
}
