"""
Unit tests for S3 Scanner
"""

import pytest
import json
from scanners.s3_scanner import S3Scanner


class TestS3Scanner:
    """Test suite for S3 security scanner"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.scanner = S3Scanner(mock_mode=True)
    
    def test_scanner_initialization(self):
        """Test that scanner initializes correctly"""
        assert self.scanner.mock_mode is True
        assert self.scanner.findings == []
    
    def test_scan_returns_findings(self):
        """Test that scan returns a list of findings"""
        findings = self.scanner.scan()
        assert isinstance(findings, list)
        assert len(findings) > 0
    
    def test_finding_structure(self):
        """Test that findings have required fields"""
        findings = self.scanner.scan()
        required_fields = ['service', 'resource', 'severity', 'issue', 'description', 'remediation']
        
        for finding in findings:
            for field in required_fields:
                assert field in finding, f"Missing field: {field}"
    
    def test_severity_levels(self):
        """Test that all findings have valid severity levels"""
        findings = self.scanner.scan()
        valid_severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        
        for finding in findings:
            assert finding['severity'] in valid_severities
    
    def test_public_bucket_detection(self):
        """Test detection of publicly accessible buckets"""
        findings = self.scanner.scan()
        
        # Should detect customer-data-backup as CRITICAL
        public_findings = [f for f in findings if 'public' in f['issue'].lower()]
        assert len(public_findings) > 0
        
        # Check for critical severity on sensitive bucket
        critical_public = [f for f in public_findings 
                          if f['severity'] == 'CRITICAL' and 'customer-data' in f['resource']]
        assert len(critical_public) > 0
    
    def test_encryption_detection(self):
        """Test detection of unencrypted buckets"""
        findings = self.scanner.scan()
        
        encryption_findings = [f for f in findings if 'encryption' in f['issue'].lower()]
        assert len(encryption_findings) > 0
    
    def test_summary_generation(self):
        """Test that summary counts findings correctly"""
        self.scanner.scan()
        summary = self.scanner.get_summary()
        
        assert 'CRITICAL' in summary
        assert 'HIGH' in summary
        assert 'MEDIUM' in summary
        assert 'LOW' in summary
        
        # Verify counts are non-negative
        for severity, count in summary.items():
            assert count >= 0
        
        # Verify total matches findings
        total = sum(summary.values())
        assert total == len(self.scanner.findings)
    
    def test_mock_data_loading(self):
        """Test that mock data loads correctly"""
        data = self.scanner.load_mock_data()
        
        assert 'buckets' in data
        assert isinstance(data['buckets'], list)
        assert len(data['buckets']) > 0
    
    def test_sensitive_bucket_detection(self):
        """Test that sensitive buckets get higher severity"""
        findings = self.scanner.scan()
        
        # Customer data bucket should have high severity for missing encryption
        customer_findings = [f for f in findings 
                           if 'customer-data-backup' in f['resource'] 
                           and 'encryption' in f['issue'].lower()]
        
        if len(customer_findings) > 0:
            assert customer_findings[0]['severity'] in ['CRITICAL', 'HIGH']
    
    def test_remediation_provided(self):
        """Test that all findings include remediation steps"""
        findings = self.scanner.scan()
        
        for finding in findings:
            assert len(finding['remediation']) > 0
            # Should contain AWS CLI command
            assert 'aws' in finding['remediation'].lower()


class TestS3ScannerEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_buckets_list(self):
        """Test handling of empty bucket list"""
        scanner = S3Scanner(mock_mode=True)
        # This would need mock data manipulation
        # Placeholder for future implementation
        pass
    
    def test_malformed_bucket_data(self):
        """Test handling of malformed bucket data"""
        # Placeholder for future implementation
        pass


# Run tests with: pytest tests/test_scanners.py -v
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
