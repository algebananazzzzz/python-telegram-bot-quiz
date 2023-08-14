terraform {
  required_version = "~>1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>4.62.0"
    }
  }

  cloud {
    workspaces {
      tags = ["github-actions"]
    }
  }
}
