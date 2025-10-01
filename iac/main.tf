resource "google_project_service" "apis_activation" {
  for_each = toset(var.needed_apis)
  project  = "chords-explorer"
  service  = each.key
}

# Cloud run service
resource "google_cloud_run_service" "backend_service" {
  name     = "chords-explorer"
  location = "europe-west9"

  template {
    spec {
      containers {
        env {
          name  = "PROJECT_ID"
          value = "chords-explorer"
        }
        # Image is pushed by Cloud Build before
        image = "europe-docker.pkg.dev/chords-explorer/chords-explorer-repository/chords-explorer"
      }
    }
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "1000"
        "run.googleapis.com/client-name"   = "terraform"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
  lifecycle {
    ignore_changes = [
      template.0.metadata.0.annotations,
    ]
  }

  depends_on = [google_project_service.apis_activation]
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location = google_cloud_run_service.backend_service.location
  project  = google_cloud_run_service.backend_service.project
  service  = google_cloud_run_service.backend_service.name

  policy_data = data.google_iam_policy.noauth.policy_data
}
