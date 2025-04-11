import os
from pathlib import Path
import json
import yaml
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentationGenerator:
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.templates_dir = Path("docs/templates")
        self.ensure_directories()
        
    def ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.output_dir,
            self.output_dir / "user_guides",
            self.output_dir / "api",
            self.output_dir / "troubleshooting",
            self.output_dir / "images",
            self.output_dir / "security",
            self.output_dir / "compliance",
            self.output_dir / "monitoring",
            self.output_dir / "deployment",
            self.templates_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def generate_user_guide(self, title: str, content: Dict[str, Any], version: str = "1.0"):
        """Generate a user guide document."""
        try:
            # Create guide directory
            guide_dir = self.output_dir / "user_guides" / title.lower().replace(" ", "_")
            guide_dir.mkdir(exist_ok=True)
            
            # Generate markdown content
            markdown = self._generate_markdown(title, content, version)
            
            # Save guide
            guide_path = guide_dir / "README.md"
            with open(guide_path, 'w') as f:
                f.write(markdown)
            
            logger.info(f"Generated user guide: {title}")
            return True
        except Exception as e:
            logger.error(f"Error generating user guide: {str(e)}")
            return False
    
    def generate_api_docs(self, endpoints: List[Dict[str, Any]], version: str = "1.0"):
        """Generate API documentation."""
        try:
            # Create API docs directory
            api_dir = self.output_dir / "api" / f"v{version}"
            api_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate OpenAPI specification
            openapi_spec = self._generate_openapi_spec(endpoints, version)
            
            # Save specification
            spec_path = api_dir / "openapi.yaml"
            with open(spec_path, 'w') as f:
                yaml.dump(openapi_spec, f, default_flow_style=False)
            
            # Generate markdown documentation
            markdown = self._generate_api_markdown(endpoints, version)
            
            # Save documentation
            docs_path = api_dir / "README.md"
            with open(docs_path, 'w') as f:
                f.write(markdown)
            
            logger.info(f"Generated API documentation v{version}")
            return True
        except Exception as e:
            logger.error(f"Error generating API documentation: {str(e)}")
            return False
    
    def generate_troubleshooting_guide(self, issues: List[Dict[str, Any]]):
        """Generate troubleshooting guide."""
        try:
            # Create troubleshooting directory
            troubleshooting_dir = self.output_dir / "troubleshooting"
            troubleshooting_dir.mkdir(exist_ok=True)
            
            # Generate markdown content
            markdown = self._generate_troubleshooting_markdown(issues)
            
            # Save guide
            guide_path = troubleshooting_dir / "README.md"
            with open(guide_path, 'w') as f:
                f.write(markdown)
            
            logger.info("Generated troubleshooting guide")
            return True
        except Exception as e:
            logger.error(f"Error generating troubleshooting guide: {str(e)}")
            return False

    def generate_security_docs(self, security_info: Dict[str, Any]):
        """Generate security documentation."""
        try:
            security_dir = self.output_dir / "security"
            security_dir.mkdir(exist_ok=True)
            
            markdown = self._generate_security_markdown(security_info)
            
            guide_path = security_dir / "README.md"
            with open(guide_path, 'w') as f:
                f.write(markdown)
            
            logger.info("Generated security documentation")
            return True
        except Exception as e:
            logger.error(f"Error generating security documentation: {str(e)}")
            return False

    def generate_compliance_docs(self, compliance_info: Dict[str, Any]):
        """Generate compliance documentation."""
        try:
            compliance_dir = self.output_dir / "compliance"
            compliance_dir.mkdir(exist_ok=True)
            
            markdown = self._generate_compliance_markdown(compliance_info)
            
            guide_path = compliance_dir / "README.md"
            with open(guide_path, 'w') as f:
                f.write(markdown)
            
            logger.info("Generated compliance documentation")
            return True
        except Exception as e:
            logger.error(f"Error generating compliance documentation: {str(e)}")
            return False

    def generate_monitoring_docs(self, monitoring_info: Dict[str, Any]):
        """Generate monitoring documentation."""
        try:
            monitoring_dir = self.output_dir / "monitoring"
            monitoring_dir.mkdir(exist_ok=True)
            
            markdown = self._generate_monitoring_markdown(monitoring_info)
            
            guide_path = monitoring_dir / "README.md"
            with open(guide_path, 'w') as f:
                f.write(markdown)
            
            logger.info("Generated monitoring documentation")
            return True
        except Exception as e:
            logger.error(f"Error generating monitoring documentation: {str(e)}")
            return False

    def _generate_security_markdown(self, security_info: Dict[str, Any]) -> str:
        """Generate markdown content for security documentation."""
        markdown = "# Security Documentation\n\n"
        markdown += f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        for section, content in security_info.items():
            markdown += f"## {section}\n\n"
            if isinstance(content, list):
                for item in content:
                    markdown += f"- {item}\n"
            elif isinstance(content, dict):
                for key, value in content.items():
                    markdown += f"### {key}\n\n{value}\n\n"
            markdown += "\n"
        
        return markdown

    def _generate_compliance_markdown(self, compliance_info: Dict[str, Any]) -> str:
        """Generate markdown content for compliance documentation."""
        markdown = "# Compliance Documentation\n\n"
        markdown += f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        for section, content in compliance_info.items():
            markdown += f"## {section}\n\n"
            if isinstance(content, list):
                for item in content:
                    markdown += f"- {item}\n"
            elif isinstance(content, dict):
                for key, value in content.items():
                    markdown += f"### {key}\n\n{value}\n\n"
            markdown += "\n"
        
        return markdown

    def _generate_monitoring_markdown(self, monitoring_info: Dict[str, Any]) -> str:
        """Generate markdown content for monitoring documentation."""
        markdown = "# Monitoring Documentation\n\n"
        markdown += f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        for section, content in monitoring_info.items():
            markdown += f"## {section}\n\n"
            if isinstance(content, list):
                for item in content:
                    markdown += f"- {item}\n"
            elif isinstance(content, dict):
                for key, value in content.items():
                    markdown += f"### {key}\n\n{value}\n\n"
            markdown += "\n"
        
        return markdown
    
    def _generate_markdown(self, title: str, content: Dict[str, Any], version: str) -> str:
        """Generate markdown content for user guide."""
        markdown = f"# {title}\n\n"
        markdown += f"Version: {version}\n"
        markdown += f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        for section, items in content.items():
            markdown += f"## {section}\n\n"
            if isinstance(items, list):
                for item in items:
                    markdown += f"- {item}\n"
            elif isinstance(items, dict):
                for key, value in items.items():
                    markdown += f"### {key}\n\n{value}\n\n"
            markdown += "\n"
        
        return markdown
    
    def _generate_openapi_spec(self, endpoints: List[Dict[str, Any]], version: str) -> Dict[str, Any]:
        """Generate OpenAPI specification."""
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'HR Analytics API',
                'version': version,
                'description': 'API documentation for HR Analytics system'
            },
            'paths': {}
        }
        
        for endpoint in endpoints:
            path = endpoint['path']
            method = endpoint['method'].lower()
            
            spec['paths'][path] = {
                method: {
                    'summary': endpoint['summary'],
                    'description': endpoint['description'],
                    'parameters': endpoint.get('parameters', []),
                    'responses': endpoint.get('responses', {})
                }
            }
        
        return spec
    
    def _generate_api_markdown(self, endpoints: List[Dict[str, Any]], version: str) -> str:
        """Generate markdown documentation for API."""
        markdown = f"# API Documentation v{version}\n\n"
        markdown += f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        for endpoint in endpoints:
            markdown += f"## {endpoint['method']} {endpoint['path']}\n\n"
            markdown += f"**Summary:** {endpoint['summary']}\n\n"
            markdown += f"**Description:** {endpoint['description']}\n\n"
            
            if 'parameters' in endpoint:
                markdown += "### Parameters\n\n"
                for param in endpoint['parameters']:
                    markdown += f"- `{param['name']}` ({param['in']}): {param['description']}\n"
                markdown += "\n"
            
            if 'responses' in endpoint:
                markdown += "### Responses\n\n"
                for status, response in endpoint['responses'].items():
                    markdown += f"- `{status}`: {response['description']}\n"
                markdown += "\n"
        
        return markdown
    
    def _generate_troubleshooting_markdown(self, issues: List[Dict[str, Any]]) -> str:
        """Generate markdown content for troubleshooting guide."""
        markdown = "# Troubleshooting Guide\n\n"
        markdown += f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        for issue in issues:
            markdown += f"## {issue['title']}\n\n"
            markdown += f"**Description:** {issue['description']}\n\n"
            
            if 'symptoms' in issue:
                markdown += "### Symptoms\n\n"
                for symptom in issue['symptoms']:
                    markdown += f"- {symptom}\n"
                markdown += "\n"
            
            if 'solutions' in issue:
                markdown += "### Solutions\n\n"
                for solution in issue['solutions']:
                    markdown += f"1. {solution}\n"
                markdown += "\n"
        
        return markdown

if __name__ == "__main__":
    # Example usage
    generator = DocumentationGenerator()
    
    # Generate user guide
    user_guide_content = {
        "Getting Started": [
            "System requirements",
            "Installation steps",
            "Initial configuration"
        ],
        "Features": {
            "Data Collection": "Description of data collection features",
            "Analytics": "Description of analytics features",
            "Reporting": "Description of reporting features"
        }
    }
    generator.generate_user_guide("User Guide", user_guide_content)
    
    # Generate API documentation
    api_endpoints = [
        {
            "path": "/api/v1/data",
            "method": "GET",
            "summary": "Get collected data",
            "description": "Retrieve collected data for analysis",
            "parameters": [
                {
                    "name": "start_date",
                    "in": "query",
                    "description": "Start date for data retrieval"
                }
            ],
            "responses": {
                "200": {
                    "description": "Successful response"
                }
            }
        }
    ]
    generator.generate_api_docs(api_endpoints)
    
    # Generate troubleshooting guide
    troubleshooting_issues = [
        {
            "title": "Data Synchronization Issues",
            "description": "Problems with data synchronization between components",
            "symptoms": [
                "Missing data points",
                "Delayed updates",
                "Inconsistent timestamps"
            ],
            "solutions": [
                "Check network connectivity",
                "Verify component status",
                "Review error logs"
            ]
        }
    ]
    generator.generate_troubleshooting_guide(troubleshooting_issues)

    # Generate security documentation
    security_info = {
        "Authentication": {
            "Password Security": "Secure password hashing using Werkzeug",
            "Session Management": "Flask-Login integration",
            "CSRF Protection": "Enabled by default"
        },
        "Data Protection": {
            "Encryption": "End-to-end encryption for data in transit and at rest",
            "Access Controls": "Role-based access control system",
            "Audit Logging": "Comprehensive audit trail for all system activities"
        }
    }
    generator.generate_security_docs(security_info)

    # Generate compliance documentation
    compliance_info = {
        "GDPR Compliance": [
            "Data minimization",
            "Right to be forgotten",
            "Data portability",
            "Privacy by design"
        ],
        "Data Retention": {
            "Policy": "Data retention periods defined per data type",
            "Implementation": "Automated cleanup procedures",
            "Audit": "Regular compliance audits"
        }
    }
    generator.generate_compliance_docs(compliance_info)

    # Generate monitoring documentation
    monitoring_info = {
        "System Monitoring": {
            "Metrics": "CPU, memory, disk usage, network I/O",
            "Alerts": "Threshold-based alerting system",
            "Logging": "Centralized logging with ELK stack"
        },
        "Performance Monitoring": {
            "Response Times": "API endpoint response time tracking",
            "Error Rates": "Error rate monitoring and alerting",
            "Resource Usage": "Resource utilization tracking"
        }
    }
    generator.generate_monitoring_docs(monitoring_info) 