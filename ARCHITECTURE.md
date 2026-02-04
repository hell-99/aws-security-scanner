# Project Architecture & Design

## Overview

AWS Security Scanner is a Python-based CLI tool designed to identify common security misconfigurations in AWS environments. The tool follows a modular architecture that allows easy extension with new security scanners.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       CLI Interface                         │
│                      (scanner.py)                           │
│  - Command-line argument parsing                            │
│  - Output formatting (Console, JSON, HTML)                  │
│  - Report generation                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Scanner Modules                           │
│                  (scanners/ package)                        │
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │ S3Scanner     │  │ EC2Scanner    │  │ IAMScanner    │  │
│  │               │  │  (planned)    │  │  (planned)    │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                │
│                                                             │
│  ┌────────────────────┐         ┌────────────────────┐     │
│  │   Mock Data        │         │   AWS Boto3 SDK    │     │
│  │  (JSON files)      │         │   (future impl)    │     │
│  └────────────────────┘         └────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. Modularity
Each service scanner (S3, EC2, IAM) is a separate module that:
- Can be developed and tested independently
- Follows a consistent interface pattern
- Returns findings in a standard format

### 2. Abstraction
The scanner supports both mock and real AWS data:
- **Mock Mode**: Uses JSON files for testing without AWS credentials
- **Real Mode**: Uses boto3 to query actual AWS resources (future)

### 3. Extensibility
Adding a new scanner requires:
1. Creating a new scanner class in `scanners/`
2. Adding mock data in `mock_data/`
3. Registering the scanner in `scanner.py`

### 4. Severity-Based Reporting
Findings are categorized by severity:
- **CRITICAL**: Immediate action required (e.g., public sensitive data)
- **HIGH**: Significant security risk (e.g., missing encryption)
- **MEDIUM**: Important but not urgent (e.g., versioning disabled)
- **LOW**: Best practice recommendations (e.g., logging disabled)

## Core Components

### 1. Scanner Base Pattern

Each scanner follows this pattern:

```python
class ServiceScanner:
    def __init__(self, mock_mode: bool = True):
        """Initialize with mock or real mode"""
        
    def scan(self) -> List[Dict[str, Any]]:
        """Run all security checks, return findings"""
        
    def _check_specific_issue(self, resource: Dict) -> None:
        """Individual security check"""
        
    def get_summary(self) -> Dict[str, int]:
        """Get severity summary"""
```

### 2. Finding Format

Standard finding structure:

```python
{
    'service': 'S3',                          # AWS service
    'resource': 'bucket-name',                # Resource identifier
    'severity': 'CRITICAL',                   # CRITICAL, HIGH, MEDIUM, LOW
    'issue': 'Public Access Enabled',         # Short issue title
    'description': 'Detailed explanation',    # Full description
    'remediation': 'CLI commands to fix'      # Step-by-step fix
}
```

### 3. CLI Interface

Uses Click for command-line interface:
- `--mock`: Enable mock mode (default: True)
- `--services`: Specify services to scan
- `--output`: Choose output format (console, json, html)
- `--report-file`: Specify output filename

### 4. Report Generation

Three output formats:
- **Console**: Colored, formatted terminal output
- **JSON**: Machine-readable for automation
- **HTML**: Professional, shareable reports

## Security Checks

### S3 Scanner

| Check | Severity Logic | Description |
|-------|----------------|-------------|
| Public Access | CRITICAL if sensitive data, LOW if tagged public | Checks ACLs for AllUsers grants |
| Public Policy | Always CRITICAL | Checks bucket policies for wildcard principals |
| Encryption | HIGH if sensitive keywords, MEDIUM otherwise | Checks default encryption status |
| Versioning | MEDIUM if critical data, LOW otherwise | Checks if versioning enabled |
| Logging | Always LOW | Checks if access logging enabled |

Sensitivity detection uses keywords: `financial`, `customer`, `personal`, `pii`, `records`, `backup`

## Future Enhancements

### Phase 2: EC2 Scanner
- Security group rules (0.0.0.0/0 on sensitive ports)
- Unencrypted EBS volumes
- IMDSv1 usage detection
- Public IP assignments

### Phase 3: IAM Scanner
- Users without MFA
- Overly permissive policies
- Unused access keys (>90 days)
- Root account usage

### Phase 4: Advanced Features
- Auto-remediation execution (with confirmation)
- Slack/email notifications
- Dashboard for trend analysis
- Integration with AWS Security Hub
- Custom compliance frameworks (PCI, HIPAA, etc.)

## Testing Strategy

### Current State
- Manual testing with mock data
- Validated against 5 different S3 bucket scenarios

### Planned
- Unit tests for each scanner module
- Integration tests with real AWS (test account)
- CI/CD pipeline for automated testing
- Code coverage reporting

## Performance Considerations

### Current
- Mock mode: Instant (no API calls)
- Scan complexity: O(n) where n = number of resources

### Future Optimizations
- Parallel scanning across services
- Caching of AWS API responses
- Rate limiting awareness
- Batch API calls where possible

## Deployment Options

### Local Development
```bash
python scanner.py --mock
```

### AWS Lambda
- Package as Lambda function
- Scheduled CloudWatch Events
- Write findings to S3/DynamoDB
- SNS notifications for critical findings

### CI/CD Integration
```yaml
# .gitlab-ci.yml or .github/workflows/
- name: Security Scan
  run: |
    python scanner.py --no-mock --output json
    # Parse and fail pipeline if critical findings
```

### Docker Container
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "scanner.py"]
```

## Contributing Guidelines

When adding new features:

1. **New Scanner**: Follow the S3Scanner pattern
2. **New Check**: Add to existing scanner, maintain severity logic
3. **Mock Data**: Create realistic test scenarios
4. **Documentation**: Update this file and README
5. **Testing**: Add unit tests (when framework ready)

## Security & Permissions

### Required IAM Permissions (Real Mode)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketPublicAccessBlock",
        "s3:GetBucketAcl",
        "s3:GetBucketPolicy",
        "s3:GetBucketVersioning",
        "s3:GetBucketLogging",
        "s3:GetEncryptionConfiguration",
        "s3:ListAllMyBuckets"
      ],
      "Resource": "*"
    }
  ]
}
```

### Best Practices
- Never commit AWS credentials
- Use IAM roles when running in AWS
- Rotate access keys regularly
- Use read-only permissions
- Enable AWS CloudTrail for audit logging

## License

MIT License - see LICENSE file for details

## Contact

For questions or contributions:
- GitHub Issues: [Report bugs or request features]
- Pull Requests: [Contribute code]
- Email: [Your contact]

---

**Built with ❤️ by Twinkle Kamdar**
