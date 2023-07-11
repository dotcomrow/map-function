terraform {
  cloud {
    organization = "dotcomrow"

    workspaces {
      name = "<PROJECT_NAME>"
    }
  }
}