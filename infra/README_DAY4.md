# Day 4 — AWS Deployment (Terraform)

Goal: get the app running on a real, Terraform-provisioned AWS EC2
instance. This directly targets the JD's AWS + IaC requirements, not
just a demo URL.

## 1. Push your code to GitHub first (if you haven't)

The EC2 instance clones your repo on boot — it needs to be pushed and
public (or you'll need to handle a deploy key, which adds complexity
we don't need for a 1-2 day timeline). Double check `.env` is
gitignored before pushing — only `.env.example` should be public.

## 2. Create your AWS account

https://aws.amazon.com/free — you will be asked for a card, this is
unavoidable even on the Free plan (it's for identity verification).
You get $100-200 in signup credits, valid 6 months.

**Cost safety, before you do anything else:**
1. AWS Console → Billing → Budgets → create a budget alert (e.g. $5)
   so you get emailed if anything unexpected happens
2. Write down today's date — plan to `terraform destroy` within your
   1-2 day window, don't leave the instance running afterward
3. A `t3.medium` running continuously costs about $0.04/hr — a full
   2 days is under $2, trivial against your credits

## 3. Install tools locally

- AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- Terraform: https://developer.hashicorp.com/terraform/install

## 4. Create an IAM user for Terraform (don't use your root account)

1. AWS Console → IAM → Users → Create user
2. Attach policy `AdministratorAccess` for now (scope this down later
   if you keep using AWS — for a 2-day demo it's fine)
3. Create an access key (CLI use case) — save the Access Key ID and
   Secret Access Key somewhere safe, shown only once
4. Configure locally:
   ```bash
   aws configure
   # paste your Access Key ID, Secret Access Key
   # region: ap-south-1
   ```

## 5. Create an EC2 key pair (for SSH)

AWS Console → EC2 → Key Pairs → Create key pair → download the
`.pem` file. On Mac/Linux: `chmod 400 your-key.pem`.

## 6. Find your public IP (to restrict SSH access)

```bash
curl ifconfig.me
```
Note it as `YOUR_IP/32` — you'll use this for `allowed_ssh_cidr`.

## 7. Run Terraform

```bash
cd infra
terraform init
terraform plan \
  -var="key_name=your-key-pair-name" \
  -var="github_repo_url=https://github.com/you/travel-agent.git" \
  -var="allowed_ssh_cidr=YOUR_IP/32"
```

Review the plan — it should show 3 resources to create (security
group, EC2 instance, elastic IP). If it looks right:

```bash
terraform apply \
  -var="key_name=your-key-pair-name" \
  -var="github_repo_url=https://github.com/you/travel-agent.git" \
  -var="allowed_ssh_cidr=YOUR_IP/32"
```

Type `yes` to confirm. This takes a few minutes — the bootstrap
script (`user_data.sh.tpl`) is installing Ollama and pulling ~5GB of
model weights in the background even after the instance shows as
"running," so don't panic if the app isn't reachable immediately.

## 8. Add your secret and start the app

```bash
ssh -i your-key-pair-name.pem ubuntu@<public_ip from terraform output>

# on the instance:
sudo tee /opt/travel-agent/.env << 'EOF'
DUFFEL_ACCESS_TOKEN=duffel_test_your_real_token
EOF

sudo systemctl start travel-agent
sudo systemctl status travel-agent   # confirm it's running
```

If it's not starting, check bootstrap logs first:
```bash
sudo cat /var/log/cloud-init-output.log
```

## 9. Visit your live demo

`terraform output streamlit_url` gives you the URL. Open it in a
browser — same app you tested locally, now running on AWS.

## End of day 4 — you should have

- [ ] A running EC2 instance, provisioned entirely by Terraform (not clicked together by hand)
- [ ] The app live at a public URL
- [ ] A billing alert set, and a plan to `terraform destroy` when you're done demoing

## Day 5 preview

CI/CD: a GitHub Actions workflow that redeploys automatically on
push, plus basic structured logging/observability — the two
remaining JD gaps.
