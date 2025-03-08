variable "github_repository" {
  description = "GitHub repository (format: owner/repo)"
  type        = string
  default     = "owner/repository"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "app"
} 