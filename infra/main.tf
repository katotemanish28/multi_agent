terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Ubuntu 22.04 LTS, always resolves to the latest AMI for the region
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_security_group" "travel_agent_sg" {
  name        = "travel-agent-sg"
  description = "SSH restricted to you; Streamlit port open for the demo"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "Streamlit demo UI"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "travel_agent" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.travel_agent_sg.id]

  root_block_device {
    volume_size = 20 # GB — model weights (~5GB) + embedding model + deps need real room
  }

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    github_repo_url = var.github_repo_url
  })

  tags = {
    Name = "travel-agent-demo"
  }
}

# Elastic IP so the demo URL doesn't change if the instance restarts.
# Free while attached to a running instance — only costs money if left
# unattached, so don't forget to release it when you tear this down.
resource "aws_eip" "travel_agent_eip" {
  instance = aws_instance.travel_agent.id
  domain   = "vpc"
}
