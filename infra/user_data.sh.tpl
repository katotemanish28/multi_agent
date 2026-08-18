#!/bin/bash
# Runs once on first boot as root (EC2 user_data). Logs to /var/log/cloud-init-output.log
# for debugging if something goes wrong.
set -e

apt-get update -y
apt-get install -y python3-pip python3-venv git

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
systemctl enable ollama
systemctl start ollama
sleep 5

export HOME=/root
ollama pull qwen2.5:0.5b
ollama pull nomic-embed-text

# Clone your app
git clone ${github_repo_url} /opt/travel-agent
cd /opt/travel-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# systemd service definition. NOT started automatically — deliberately.
# Secrets (DUFFEL_ACCESS_TOKEN) are never baked into user_data or Terraform
# state, since both can end up visible in the AWS console or a repo. SSH in
# after boot, create /opt/travel-agent/.env by hand, then start this service.
cat > /etc/systemd/system/travel-agent.service << 'EOF'
[Unit]
Description=Travel Agent Streamlit App
After=network.target ollama.service

[Service]
Type=simple
WorkingDirectory=/opt/travel-agent
ExecStart=/opt/travel-agent/venv/bin/streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=on-failure
EnvironmentFile=/opt/travel-agent/.env

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable travel-agent

echo "Bootstrap complete. SSH in, create /opt/travel-agent/.env with your DUFFEL_ACCESS_TOKEN, then: sudo systemctl start travel-agent"
