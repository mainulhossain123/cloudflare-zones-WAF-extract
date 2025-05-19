# 🚀 Cloudflare Zones WAF Rules Extractor

This script extracts **Custom Firewall Rules** from all **Cloudflare Zones** under a specific account and filters them by user-defined rule action (e.g., `skip`, `block`, `challenge`). It generates a detailed CSV report for further analysis or audit automation.

Built for **enterprise scalability**, it supports parallel processing, retry logic, and secure token-based access. Ideal for DevOps, SecOps, and cloud governance use cases.

---

## 📦 Features

- 🔍 Fetches **Custom HTTP Firewall Rules** per zone
- ⚙️ Filters rules by **action** (e.g., `skip`, `block`, etc.)
- 📄 Exports data into a **timestamped CSV**
- 🧵 Parallel zone processing using `ThreadPoolExecutor`
- 🔁 Built-in retry logic for API resilience
- ✅ Ready for **enterprise pipelines** (CI/CD, CRON, GitHub Actions)

---

## 🧾 CSV Output

Each rule is saved with the following fields:

| Zone Name | Rule ID | Version | Action | Expression | Description | Last Updated | Enabled |
|-----------|---------|---------|--------|------------|-------------|--------------|---------|

📁 Example output filename: firewall_custom_rules_2025-05-19.csv


---

## 🔐 Environment Variables

| Variable        | Description                                             | Required | Default           |
|----------------|---------------------------------------------------------|----------|-------------------|
| `API_KEY`       | Cloudflare API token with zone/ruleset read permissions | ✅       | –                 |
| `ACCOUNT_NAME`  | Cloudflare account name to scope zone fetch             | ✅       | `DXP Customers`   |
| `RULE_ACTION`   | Rule action to filter for (`skip`, `block`, `challenge`)| ❌       | `skip`            |

Set these in your shell or CI/CD environment.

```bash
export API_KEY="your_token_here"
export ACCOUNT_NAME="Your Cloudflare Account Name"
export RULE_ACTION="skip"
```

⚙️ How to Use
1. Install Dependencies
```bash
pip install requests
```

2. Clone and Navigate
```bash
git clone https://github.com/mainulhossain123/cloudflare-zones-WAF-extract.git
cd cloudflare-zones-WAF-extract
```

3. Run the Script
```bash
python CF_Zones_WAF_Extract.py
```

This creates a CSV file in /app/, containing rule data filtered by your RULE_ACTION.


💡 Deployment Tips
This script is designed to run:

* As a scheduled cron job

* Inside a Docker container

* Through CI/CD pipelines (e.g., GitHub Actions)

* In Kubernetes Jobs for periodic audits

🔒 Security Tip: Use secrets management tools (e.g., GitHub Secrets, AWS SSM, Azure Key Vault) to inject API_KEY.

🧰 API Access Requirements
Your API token must include:

* Zone:Read

* Zone Rulesets: Read

🧪 Sample Output Logs

```yaml
Zone Name: example.com, Rule ID: 82ab23..., Action: skip
Zone Name: anotherdomain.org, Rule ID: c3fd98..., Action: skip
```

🛠️ Best Practices
* 🧵 Tune max_workers in ThreadPoolExecutor based on API rate limits

* 📊 Run monthly for firewall auditing

* 📁 Store CSV outputs in S3, Azure Blob, or GCS for long-term access

* 🚨 Integrate with Slack/email alerts if high-risk rules are found


🤝 Contributing
We follow enterprise standards for contributions:

* Fork the repo

* Create a feature branch (feature/my-feature)

* Commit with clear messages and submit a PR

* Follow PEP8 and Pythonic best practices
