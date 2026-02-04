#!/usr/bin/env python3
"""
AWS Security Scanner - Main CLI Entry Point
"""

import click
import json
from datetime import datetime
from colorama import Fore, Style, init
from scanners.s3_scanner import S3Scanner

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def print_banner():
    """Print ASCII banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║        AWS Security Posture Scanner v1.0              ║               
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner)


def get_severity_color(severity: str) -> str:
    """Get color code for severity level"""
    color_map = {
        'CRITICAL': Fore.RED,
        'HIGH': Fore.LIGHTRED_EX,
        'MEDIUM': Fore.YELLOW,
        'LOW': Fore.BLUE
    }
    return color_map.get(severity, Fore.WHITE)


def print_finding(finding: dict, index: int):
    """Pretty print a security finding"""
    severity = finding.get('severity', 'UNKNOWN')
    color = get_severity_color(severity)
    
    print(f"\n{color}{'═' * 70}")
    print(f"[{index + 1}] [{severity}] {finding.get('issue', 'Unknown Issue')}")
    print(f"{'═' * 70}{Style.RESET_ALL}")
    
    print(f"  Service:     {finding.get('service', 'N/A')}")
    print(f"  Resource:    {finding.get('resource', 'N/A')}")
    print(f"  Description: {finding.get('description', 'N/A')}")
    print(f"\n  Remediation:")
    print(f"  {finding.get('remediation', 'N/A')}")


def print_summary(summary: dict):
    """Print summary of findings"""
    total = sum(summary.values())
    
    print(f"\n{Fore.CYAN}{'═' * 70}")
    print(f"SCAN SUMMARY")
    print(f"{'═' * 70}{Style.RESET_ALL}\n")
    
    if total == 0:
        print(f"{Fore.GREEN}✓ No security issues found! Your AWS environment looks good.{Style.RESET_ALL}\n")
        return
    
    print(f"Total Issues Found: {total}\n")
    print(f"{Fore.RED}  Critical: {summary.get('CRITICAL', 0)}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}  High:     {summary.get('HIGH', 0)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  Medium:   {summary.get('MEDIUM', 0)}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}  Low:      {summary.get('LOW', 0)}{Style.RESET_ALL}\n")


def generate_json_report(findings: list, output_file: str):
    """Generate JSON report of findings"""
    report = {
        'scan_date': datetime.now().isoformat(),
        'scanner_version': '1.0',
        'total_findings': len(findings),
        'findings': findings
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"{Fore.GREEN}✓ JSON report saved to: {output_file}{Style.RESET_ALL}")


def generate_html_report(findings: list, summary: dict, output_file: str):
    """Generate HTML report of findings"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AWS Security Scan Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin: 20px 0;
            }}
            .summary-box {{
                padding: 20px;
                border-radius: 5px;
                text-align: center;
            }}
            .critical {{ background-color: #e74c3c; color: white; }}
            .high {{ background-color: #e67e22; color: white; }}
            .medium {{ background-color: #f39c12; color: white; }}
            .low {{ background-color: #3498db; color: white; }}
            .finding {{
                border-left: 4px solid;
                padding: 20px;
                margin: 15px 0;
                background-color: #ffffff;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .finding.critical {{ border-left-color: #e74c3c; }}
            .finding.high {{ border-left-color: #e67e22; }}
            .finding.medium {{ border-left-color: #f39c12; }}
            .finding.low {{ border-left-color: #3498db; }}
            .finding-header {{
                font-weight: bold;
                font-size: 1.2em;
                margin-bottom: 15px;
                color: #2c3e50;
            }}
            .badge {{
                display: inline-block;
                padding: 5px 12px;
                border-radius: 3px;
                font-size: 0.85em;
                font-weight: bold;
                margin-right: 10px;
                color: white;
            }}
            .badge.critical {{ background-color: #e74c3c; }}
            .badge.high {{ background-color: #e67e22; }}
            .badge.medium {{ background-color: #f39c12; }}
            .badge.low {{ background-color: #3498db; }}
            .remediation {{
                background-color: #ecf0f1;
                padding: 15px;
                margin-top: 15px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
            }}
            .timestamp {{
                color: #7f8c8d;
                font-size: 0.9em;
            }}
            h2 {{
                color: #2c3e50;
                margin-top: 30px;
                margin-bottom: 20px;
            }}
            .finding p {{
                color: #34495e;
                line-height: 1.6;
                margin: 8px 0;
            }}
            .finding strong {{
                color: #2c3e50;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AWS Security Scan Report</h1>
            <p class="timestamp">Generated: {scan_date}</p>
            
            <div class="summary">
                <div class="summary-box critical">
                    <h2>{critical}</h2>
                    <p>Critical</p>
                </div>
                <div class="summary-box high">
                    <h2>{high}</h2>
                    <p>High</p>
                </div>
                <div class="summary-box medium">
                    <h2>{medium}</h2>
                    <p>Medium</p>
                </div>
                <div class="summary-box low">
                    <h2>{low}</h2>
                    <p>Low</p>
                </div>
            </div>
            
            <h2>Findings</h2>
            {findings_html}
        </div>
    </body>
    </html>
    """
    
    findings_html = ""
    for i, finding in enumerate(findings, 1):
        severity = finding.get('severity', 'UNKNOWN').lower()
        findings_html += f"""
        <div class="finding {severity}">
            <div class="finding-header">
                <span class="badge {severity}">{finding.get('severity', 'UNKNOWN')}</span>
                {finding.get('issue', 'Unknown Issue')}
            </div>
            <p><strong>Service:</strong> {finding.get('service', 'N/A')}</p>
            <p><strong>Resource:</strong> {finding.get('resource', 'N/A')}</p>
            <p><strong>Description:</strong> {finding.get('description', 'N/A')}</p>
            <div class="remediation">
                <strong>Remediation:</strong><br>
                {finding.get('remediation', 'N/A')}
            </div>
        </div>
        """
    
    html_content = html_template.format(
        scan_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        critical=summary.get('CRITICAL', 0),
        high=summary.get('HIGH', 0),
        medium=summary.get('MEDIUM', 0),
        low=summary.get('LOW', 0),
        findings_html=findings_html
    )
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"{Fore.GREEN} HTML report saved to: {output_file}{Style.RESET_ALL}")


@click.command()
@click.option('--mock', 'mock', flag_value=True, default=True, help='Run in mock mode (no AWS credentials needed)')
@click.option('--no-mock', 'mock', flag_value=False, help='Run against real AWS')
@click.option('--services', default='s3', help='Comma-separated list of services to scan (e.g., s3,ec2,iam)')
@click.option('--output', type=click.Choice(['console', 'json', 'html']), default='console', 
              help='Output format')
@click.option('--report-file', default='security-report', help='Output filename (without extension)')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def main(mock, services, output, report_file, verbose):
    """
    AWS Security Posture Scanner
    
    Scan your AWS environment for common security misconfigurations.
    """
    print_banner()
    
    if mock:
        print(f"{Fore.YELLOW}ℹ Running in MOCK mode (using sample data){Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}ℹ Running against real AWS environment{Style.RESET_ALL}")
    
    print(f"Services to scan: {services}\n")
    
    all_findings = []
    service_list = [s.strip().lower() for s in services.split(',')]
    
    # Run S3 scanner
    if 's3' in service_list:
        print(f"{Fore.CYAN}Scanning S3 buckets...{Style.RESET_ALL}")
        s3_scanner = S3Scanner(mock_mode=mock)
        s3_findings = s3_scanner.scan()
        all_findings.extend(s3_findings)
        
        if verbose:
            print(f"  Found {len(s3_findings)} S3 issues")
    
    # TODO: Add EC2 scanner
    # TODO: Add IAM scanner
    
    # Sort findings by severity
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    all_findings.sort(key=lambda x: severity_order.get(x.get('severity', 'LOW'), 4))
    
    # Generate output based on format
    if output == 'console':
        for i, finding in enumerate(all_findings):
            print_finding(finding, i)
        
        # Generate summary
        s3_scanner = S3Scanner(mock_mode=mock)
        s3_scanner.findings = all_findings
        summary = s3_scanner.get_summary()
        print_summary(summary)
        
    elif output == 'json':
        json_file = f"{report_file}.json"
        generate_json_report(all_findings, json_file)
        
    elif output == 'html':
        html_file = f"{report_file}.html"
        s3_scanner = S3Scanner(mock_mode=mock)
        s3_scanner.findings = all_findings
        summary = s3_scanner.get_summary()
        generate_html_report(all_findings, summary, html_file)
    
    # Print recommendation
    if len(all_findings) > 0:
        print(f"\n{Fore.YELLOW}💡 Tip: Use --output json or --output html to generate reports for your security team{Style.RESET_ALL}\n")


if __name__ == '__main__':
    main()
