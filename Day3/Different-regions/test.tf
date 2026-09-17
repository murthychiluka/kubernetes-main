# multiple AWS provider configurations with aliases.

provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu"
  region = "eu-west-1"
}

resource "aws_s3_bucket" "us_bucket" {
  bucket = "my-company-us-bucket"
}

resource "aws_s3_bucket" "eu_bucket" {
  provider = aws.eu
  bucket   = "my-company-eu-bucket"
}
