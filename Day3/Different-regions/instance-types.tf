#different EC2 instance sizes for dev, staging, and prod
# terraform apply -var="environment=dev"

resource "aws_instance" "name" {
    ami           = "ami-0e34b50e714a297f1"
    instance_type = var.instance_type[var.environment]
}

variable "instance_type" {
  description = "The type of instance to use"
  type        = map(string)
  default     = {
    dev  = "t3.micro"
    prod = "t2.medium"
  }
}
 variable "environment" {
  description = "The environment to deploy to"
  type        = string
 }
