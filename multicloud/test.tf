provider "aws" {
  region = "us-east-1"
}

provider "azurerm" {
  features {}
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "murthy-aws-demo-bucket"
}

resource "azurerm_resource_group" "my_rg" {
  name     = "rg-murthy143-demo"
  location = "West US 2"
}
