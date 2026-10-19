terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "DisasterReliefResourceAllocationPlatform"
      Environment = var.environment
      Owner       = "Kini Prathamesh Prakash (124BTCS1057)"
      ManagedBy   = "Terraform"
      SDG         = "SDG-11"
      Course      = "CO2"
    }
  }
}
