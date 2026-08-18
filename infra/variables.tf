variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-south-1" # Mumbai — lowest latency from India
}

variable "instance_type" {
  description = "EC2 instance type. Must have enough RAM for llama3.1:8b (~5-6GB) — t3.micro (1GB) will NOT work."
  type        = string
  default     = "t3.micro" # 4GB RAM, ~$0.04/hr — a couple of demo days costs a few dollars, covered by free-tier credits
}

variable "key_name" {
  description = "Name of an EC2 key pair you've already created in the AWS console, for SSH access"
  type        = string
}

variable "github_repo_url" {
  description = "HTTPS URL of your pushed travel-agent repo, e.g. https://github.com/you/travel-agent.git"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "Your current public IP in CIDR form, e.g. 49.36.XX.XX/32 — restricts SSH to just you, not the whole internet"
  type        = string
}
