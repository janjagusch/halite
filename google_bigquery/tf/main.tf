provider "google" {
  project = "kaggle-halite"
}

data "google_project" "kaggle_halite" {
  project_id = "kaggle-halite"
}


resource "google_bigquery_dataset" "halite_analytics" {
  dataset_id                  = "halite_analytics"
  friendly_name               = "halite_analytics"
  description                 = "Stores analytical data about Halite matches."
  location                    = var.dataset__location

  access {
    role          = "OWNER"
    user_by_email = "jan.jagusch@gmail.com"
  }

  access {
    role          = "WRITER"
    user_by_email = "haakon.robinson@gmail.com"
  }
}

resource "google_bigquery_table" "dim_game" {
  dataset_id = "halite_analytics"
  table_id   = "dim_game"
  schema     = file("../datasets/halite_analytics/tables/dim_game.json")
}

resource "google_bigquery_table" "dim_player" {
  dataset_id = "halite_analytics"
  table_id   = "dim_player"
  schema     = file("../datasets/halite_analytics/tables/dim_player.json")
}

resource "google_bigquery_table" "fact" {
  dataset_id = "halite_analytics"
  table_id   = "fact"
  schema     = file("../datasets/halite_analytics/tables/fact.json")
}
