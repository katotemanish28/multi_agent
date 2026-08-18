output "public_ip" {
  value = aws_eip.travel_agent_eip.public_ip
}

output "streamlit_url" {
  value = "http://${aws_eip.travel_agent_eip.public_ip}:8501"
}

output "ssh_command" {
  value = "ssh -i /path/to/${var.key_name}.pem ubuntu@${aws_eip.travel_agent_eip.public_ip}"
}
