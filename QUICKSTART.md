# Quick Start Guide

Get up and running with AWS Security Scanner in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/aws-security-scanner.git
cd aws-security-scanner

# Install dependencies
pip install -r requirements.txt
```

## Try It Out (No AWS Account Needed!)

Run the scanner in mock mode to see how it works:

```bash
python scanner.py --mock
```

This will scan mock AWS data and show you security findings with color-coded severity levels.

## Generate Reports

### HTML Report (Recommended for presentations)
```bash
python scanner.py --mock --output html --report-file my-security-report
```

This creates a professional HTML report at `my-security-report.html` that you can open in any browser.

### JSON Report (For automation/CI-CD)
```bash
python scanner.py --mock --output json --report-file my-security-report
```

This creates a machine-readable JSON report at `my-security-report.json`.

## Connect to Real AWS (Optional)

### Prerequisites
- AWS Account
- AWS CLI configured with credentials
- Appropriate IAM permissions (ReadOnly access to S3, EC2, IAM)

### Setup AWS Credentials

**Option 1: AWS CLI**
```bash
aws configure
```

**Option 2: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Run Against Real AWS
```bash
# Scan all services
python scanner.py --no-mock

# Scan specific services
python scanner.py --no-mock --services s3,ec2,iam

# Generate HTML report
python scanner.py --no-mock --output html --report-file aws-scan-$(date +%Y%m%d)
```

## What Gets Scanned?

### S3 Buckets
- Public access settings
- Encryption status
- Versioning configuration
- Access logging
- Bucket policies

### EC2 (Coming Soon)
- Security group rules
- Unencrypted EBS volumes
- Public IP assignments
- Instance metadata service version

### IAM (Coming Soon)
- Users without MFA
- Overly permissive policies
- Unused access keys
- Password policies

## Pro Tips

1. **Start with Mock Mode**: Get familiar with the tool before scanning real AWS
2. **Generate HTML Reports**: Perfect for presenting findings to your team
3. **Schedule Regular Scans**: Set up cron jobs for continuous monitoring
4. **Prioritize Critical Issues**: Focus on CRITICAL and HIGH severity findings first

## Troubleshooting

**Error: "No module named 'colorama'"**
```bash
pip install -r requirements.txt
```

**Error: "Unable to locate credentials"**
- Run `aws configure` to set up your AWS credentials
- Or use the `--mock` flag to run without AWS access

**Permission Denied**
```bash
chmod +x scanner.py
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to add new features
- Open an issue if you find bugs or have suggestions

Happy scanning! 
