provider "aws" {
  region = "us-west-2"
}

# variables
variable "lambda_version"     { default = "1.0.0"}