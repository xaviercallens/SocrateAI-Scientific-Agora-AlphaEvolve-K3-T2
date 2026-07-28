# GCP Agent Kit & Antigravity TPU Provisioning
terraform {
  required_version = ">= 1.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}

variable "gcp_project_id" {
  type        = string
  default     = "gen-lang-client-0625573011"
  description = "GCP Project ID for SocrateAI Antigravity & Agent Kit deployment"
}

variable "gcp_region" {
  type        = string
  default     = "us-central1"
  description = "Primary GCP Region"
}

variable "gcp_zone" {
  type        = string
  default     = "us-central2-b"
  description = "GCP Zone for TPU Pod Slices"
}

resource "google_service_account" "alphaevolve_runner_sa" {
  account_id   = "alphaevolve-runner-sa"
  display_name = "AlphaEvolve Vertex AI Runner Service Account"
}

resource "google_compute_instance" "antigravity_tpu_node" {
  name         = "socrateai-antigravity-node-1"
  machine_type = "ct4p-hightcpu-4t" # TPU v4 pod slice
  zone         = var.gcp_zone

  boot_disk {
    initialize_params {
      image = "projects/ml-images/global/images/c0-deeplearning-tpu-ubuntu2204"
    }
  }
  
  service_account {
    email  = google_service_account.alphaevolve_runner_sa.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

# Vertex AI Custom Job for AlphaEvolve (CY4 Metric Approximation Search)
resource "google_vertex_ai_custom_job" "alphaevolve_cy4_metric" {
  display_name = "alphaevolve-cy4-metric-search"
  region       = var.gcp_region

  job_spec {
    service_account = google_service_account.alphaevolve_runner_sa.email

    worker_pool_specs {
      machine_spec {
        machine_type      = "n1-standard-8"
        accelerator_type  = "NVIDIA_TESLA_V100"
        accelerator_count = 2
      }
      replica_count = 1
      container_spec {
        image_uri = "us-central1-docker.pkg.dev/${var.gcp_project_id}/stream2-alphaevolve/cy4-metric-search:latest"
        command   = ["python3", "-m", "pipeline.alphaevolve_search.cy4_metric_search"]
        env {
          name  = "GCS_DATA_LAKE_BUCKET"
          value = "gs://socrateai-datalake-${var.gcp_project_id}"
        }
        env {
          name  = "GCP_PROJECT_ID"
          value = var.gcp_project_id
        }
      }
    }
  }
}
