"""
S3 Security Scanner
Checks for common S3 misconfigurations and security issues
"""

import json
from typing import List, Dict, Any


class S3Scanner:
    """Scanner for S3 bucket security issues"""
    
    SEVERITY_CRITICAL = "CRITICAL"
    SEVERITY_HIGH = "HIGH"
    SEVERITY_MEDIUM = "MEDIUM"
    SEVERITY_LOW = "LOW"
    
    def __init__(self, mock_mode: bool = True):
        """
        Initialize S3 scanner
        
        Args:
            mock_mode: If True, use mock data instead of real AWS API calls
        """
        self.mock_mode = mock_mode
        self.findings = []
    
    def load_mock_data(self) -> Dict[str, Any]:
        """Load mock S3 data from JSON file"""
        with open('mock_data/s3_mock.json', 'r') as f:
            return json.load(f)
    
    def scan(self) -> List[Dict[str, Any]]:
        """
        Run all S3 security checks
        
        Returns:
            List of security findings
        """
        self.findings = []
        
        if self.mock_mode:
            data = self.load_mock_data()
            buckets = data.get('buckets', [])
        else:
            # TODO: Need to implement real AWS API calls using boto3
            buckets = []
        
        for bucket in buckets:
            self._check_public_access(bucket)
            self._check_encryption(bucket)
            self._check_versioning(bucket)
            self._check_logging(bucket)
            self._check_public_policy(bucket)
        
        return self.findings
    
    def _check_public_access(self, bucket: Dict[str, Any]) -> None:
        """Check if bucket allows public access via ACLs"""
        bucket_name = bucket.get('name')
        acl = bucket.get('acl', {})
        grants = acl.get('grants', [])
        
        # Check if bucket has public read access
        for grant in grants:
            grantee = grant.get('grantee', {})
            if grantee.get('type') == 'Group' and 'AllUsers' in grantee.get('uri', ''):
                # Check if this is intentional (tagged as public website)
                tags = bucket.get('tags', [])
                is_public_website = any(
                    tag.get('key') == 'Purpose' and 'public' in tag.get('value', '').lower()
                    for tag in tags
                )
                
                if is_public_website:
                    severity = self.SEVERITY_LOW
                    description = f"S3 bucket '{bucket_name}' is publicly accessible (tagged as public website)"
                else:
                    severity = self.SEVERITY_CRITICAL
                    description = f"S3 bucket '{bucket_name}' is publicly accessible and may contain sensitive data"
                
                self.findings.append({
                    'service': 'S3',
                    'resource': bucket_name,
                    'severity': severity,
                    'issue': 'Public Access Enabled',
                    'description': description,
                    'remediation': f"Block public access for bucket '{bucket_name}' unless absolutely necessary. "
                                 f"Use AWS CLI: aws s3api put-public-access-block --bucket {bucket_name} "
                                 f"--public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,"
                                 f"BlockPublicPolicy=true,RestrictPublicBuckets=true"
                })
    
    def _check_encryption(self, bucket: Dict[str, Any]) -> None:
        """Check if bucket has encryption enabled"""
        bucket_name = bucket.get('name')
        encryption = bucket.get('encryption')
        
        if not encryption:
            # Check bucket naming to determine sensitivity
            sensitive_keywords = ['financial', 'customer', 'personal', 'pii', 'records', 'backup']
            is_sensitive = any(keyword in bucket_name.lower() for keyword in sensitive_keywords)
            
            severity = self.SEVERITY_HIGH if is_sensitive else self.SEVERITY_MEDIUM
            
            self.findings.append({
                'service': 'S3',
                'resource': bucket_name,
                'severity': severity,
                'issue': 'Encryption Not Enabled',
                'description': f"S3 bucket '{bucket_name}' does not have default encryption enabled",
                'remediation': f"Enable default encryption for bucket '{bucket_name}'. "
                             f"Use AWS CLI: aws s3api put-bucket-encryption --bucket {bucket_name} "
                             f"--server-side-encryption-configuration "
                             f"'{{\"Rules\":[{{\"ApplyServerSideEncryptionByDefault\":{{\"SSEAlgorithm\":\"AES256\"}}}}]}}'"
            })
    
    def _check_versioning(self, bucket: Dict[str, Any]) -> None:
        """Check if bucket has versioning enabled"""
        bucket_name = bucket.get('name')
        versioning = bucket.get('versioning', 'Disabled')
        
        if versioning != 'Enabled':
            # Versioning is important for compliance and data recovery
            sensitive_keywords = ['backup', 'records', 'financial', 'compliance']
            is_critical_data = any(keyword in bucket_name.lower() for keyword in sensitive_keywords)
            
            severity = self.SEVERITY_MEDIUM if is_critical_data else self.SEVERITY_LOW
            
            self.findings.append({
                'service': 'S3',
                'resource': bucket_name,
                'severity': severity,
                'issue': 'Versioning Disabled',
                'description': f"S3 bucket '{bucket_name}' does not have versioning enabled. "
                             f"This increases risk of accidental data loss.",
                'remediation': f"Enable versioning for bucket '{bucket_name}'. "
                             f"Use AWS CLI: aws s3api put-bucket-versioning --bucket {bucket_name} "
                             f"--versioning-configuration Status=Enabled"
            })
    
    def _check_logging(self, bucket: Dict[str, Any]) -> None:
        """Check if bucket has access logging enabled"""
        bucket_name = bucket.get('name')
        logging = bucket.get('logging', False)
        
        if not logging:
            # Logging is important for audit trails and compliance
            self.findings.append({
                'service': 'S3',
                'resource': bucket_name,
                'severity': self.SEVERITY_LOW,
                'issue': 'Access Logging Disabled',
                'description': f"S3 bucket '{bucket_name}' does not have access logging enabled. "
                             f"This makes it difficult to audit access patterns and investigate incidents.",
                'remediation': f"Enable access logging for bucket '{bucket_name}'. "
                             f"First create a logging bucket, then use AWS CLI: "
                             f"aws s3api put-bucket-logging --bucket {bucket_name} "
                             f"--bucket-logging-status file://logging.json"
            })
    
    def _check_public_policy(self, bucket: Dict[str, Any]) -> None:
        """Check if bucket has a policy that allows public access"""
        bucket_name = bucket.get('name')
        policy = bucket.get('bucket_policy')
        
        if policy:
            statements = policy.get('Statement', [])
            for statement in statements:
                principal = statement.get('Principal')
                effect = statement.get('Effect', '')
                
                # Check for wildcard principal with Allow effect
                if principal == '*' and effect == 'Allow':
                    self.findings.append({
                        'service': 'S3',
                        'resource': bucket_name,
                        'severity': self.SEVERITY_CRITICAL,
                        'issue': 'Public Bucket Policy',
                        'description': f"S3 bucket '{bucket_name}' has a bucket policy that allows public access "
                                     f"(Principal: '*'). This overrides bucket ACL settings.",
                        'remediation': f"Review and restrict the bucket policy for '{bucket_name}'. "
                                     f"Remove or narrow the Principal field. Consider using AWS Organizations "
                                     f"SCPs to prevent public bucket policies."
                    })
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary of findings by severity"""
        summary = {
            self.SEVERITY_CRITICAL: 0,
            self.SEVERITY_HIGH: 0,
            self.SEVERITY_MEDIUM: 0,
            self.SEVERITY_LOW: 0
        }
        
        for finding in self.findings:
            severity = finding.get('severity')
            if severity in summary:
                summary[severity] += 1
        
        return summary
