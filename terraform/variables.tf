variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "resume-builder"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"

}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "asg_desired_capacity" {
  description = "Desired number of instances in ASG"
  type        = number
  default     = 2
}

variable "asg_min_size" {
  description = "Minimum number of instances in ASG"
  type        = number
  default     = 1
}

variable "asg_max_size" {
  description = "Maximum number of instances in ASG"
  type        = number
  default     = 4

}

variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string


variable "asg_max_size" {
  description = "Maximum number of instances in ASG"
  type        = number
  default     = 4

}

variable "github_repository" {
  description = "GitHub repository (format: owner/repo)"
  type        = string
  default     = "5heyda/AWSCvGenerator"
} 