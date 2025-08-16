import openai
from typing import List, Dict, Optional
import asyncio
import logging
from jinja2 import Template

from app.core.config import settings

logger = logging.getLogger(__name__)

class DocumentationGenerator:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.AsyncOpenAI()
        
    async def generate_documentation(self, repository_data: Dict[str, any]) -> Dict[str, str]:
        """Generate comprehensive documentation for repository"""
        try:
            # Analyze repository structure
            structure_analysis = await self._analyze_repository_structure(repository_data)
            
            # Generate different sections
            tasks = [
                self._generate_overview(repository_data, structure_analysis),
                self._generate_api_docs(repository_data, structure_analysis),
                self._generate_setup_guide(repository_data, structure_analysis),
                self._generate_architecture_docs(repository_data, structure_analysis)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            documentation = {
                'overview': results[0] if not isinstance(results[0], Exception) else "Could not generate overview",
                'api_documentation': results[1] if not isinstance(results[1], Exception) else "Could not generate API docs",
                'setup_guide': results[2] if not isinstance(results[2], Exception) else "Could not generate setup guide",
                'architecture': results[3] if not isinstance(results[3], Exception) else "Could not generate architecture docs"
            }
            
            return documentation
            
        except Exception as e:
            logger.error(f"Documentation generation error: {str(e)}")
            raise ValueError(f"Failed to generate documentation: {str(e)}")
    
    async def generate_faq(self, repository_data: Dict[str, any]) -> List[Dict[str, str]]:
        """Generate FAQ based on repository content"""
        try:
            # Analyze common patterns and potential questions
            code_analysis = await self._analyze_code_patterns(repository_data)
            
            prompt = f"""
            Based on this repository analysis, generate a comprehensive FAQ with questions developers commonly ask about this type of project.
            
            Repository: {repository_data['name']}
            Description: {repository_data.get('description', 'No description')}
            Main Language: {repository_data.get('language', 'Unknown')}
            
            Code Analysis:
            {code_analysis}
            
            Generate 8-12 FAQ items in JSON format with 'question' and 'answer' fields.
            Focus on:
            - Setup and installation
            - Common usage patterns
            - Configuration options
            - Troubleshooting
            - API usage (if applicable)
            - Contributing guidelines
            
            Return valid JSON array format.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical documentation expert. Generate practical, helpful FAQ items based on code analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse JSON response
            import json
            faq_data = json.loads(response.choices[0].message.content)
            
            return faq_data
            
        except Exception as e:
            logger.error(f"FAQ generation error: {str(e)}")
            # Return default FAQ if generation fails
            return [
                {
                    "question": "How do I install and set up this project?",
                    "answer": "Please refer to the README file or setup guide for installation instructions."
                },
                {
                    "question": "What are the main dependencies?",
                    "answer": "Check the requirements.txt, package.json, or similar dependency files in the repository."
                },
                {
                    "question": "How do I contribute to this project?",
                    "answer": "Please check if there's a CONTRIBUTING.md file or contact the maintainers."
                }
            ]
    
    async def _analyze_repository_structure(self, repository_data: Dict[str, any]) -> str:
        """Analyze repository structure and extract key information"""
        try:
            files = repository_data.get('files', [])
            
            # Categorize files
            categories = {
                'config': [],
                'source': [],
                'tests': [],
                'docs': [],
                'scripts': []
            }
            
            for file in files:
                path = file['path'].lower()
                if any(config in path for config in ['config', '.env', 'settings', 'package.json', 'requirements']):
                    categories['config'].append(file['path'])
                elif any(test in path for test in ['test', 'spec', '__test__']):
                    categories['tests'].append(file['path'])
                elif any(doc in path for doc in ['readme', 'doc', 'md']):
                    categories['docs'].append(file['path'])
                elif any(script in path for script in ['script', 'bin', 'tool']):
                    categories['scripts'].append(file['path'])
                else:
                    categories['source'].append(file['path'])
            
            structure = f"""
            Repository Structure Analysis:
            - Configuration files: {len(categories['config'])} files
            - Source code files: {len(categories['source'])} files  
            - Test files: {len(categories['tests'])} files
            - Documentation files: {len(categories['docs'])} files
            - Script files: {len(categories['scripts'])} files
            
            Key files found:
            {categories['config'][:5]}
            {categories['source'][:10]}
            """
            
            return structure
            
        except Exception as e:
            logger.error(f"Structure analysis error: {str(e)}")
            return "Could not analyze repository structure"
    
    async def _generate_overview(self, repository_data: Dict[str, any], structure: str) -> str:
        """Generate project overview documentation"""
        prompt = f"""
        Generate a comprehensive project overview for this repository:
        
        Name: {repository_data['name']}
        Description: {repository_data.get('description', 'No description')}
        Language: {repository_data.get('language', 'Unknown')}
        
        {structure}
        
        Include:
        1. Project purpose and goals
        2. Key features and capabilities
        3. Technology stack
        4. Target audience
        5. Current status and maturity level
        
        Format as markdown with clear sections.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a technical writer creating project documentation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    async def _generate_api_docs(self, repository_data: Dict[str, any], structure: str) -> str:
        """Generate API documentation if applicable"""
        # Check if this looks like an API project
        files = repository_data.get('files', [])
        api_indicators = ['api', 'route', 'endpoint', 'handler', 'controller']
        
        has_api = any(
            any(indicator in file['path'].lower() for indicator in api_indicators)
            for file in files
        )
        
        if not has_api:
            return "This repository does not appear to contain API endpoints."
        
        prompt = f"""
        Generate API documentation for this repository:
        
        {structure}
        
        Based on the file structure, document:
        1. Available endpoints (if detectable)
        2. Request/response formats
        3. Authentication requirements
        4. Error handling
        5. Usage examples
        
        Format as markdown with clear sections.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an API documentation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    async def _generate_setup_guide(self, repository_data: Dict[str, any], structure: str) -> str:
        """Generate setup and installation guide"""
        prompt = f"""
        Generate a setup and installation guide for:
        
        Name: {repository_data['name']}
        Language: {repository_data.get('language', 'Unknown')}
        
        {structure}
        
        Include:
        1. Prerequisites and dependencies
        2. Installation steps
        3. Configuration requirements
        4. Environment setup
        5. Verification steps
        6. Common issues and troubleshooting
        
        Format as markdown with step-by-step instructions.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a technical writer creating setup guides."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1200
        )
        
        return response.choices[0].message.content
    
    async def _generate_architecture_docs(self, repository_data: Dict[str, any], structure: str) -> str:
        """Generate architecture documentation"""
        prompt = f"""
        Generate architecture documentation for:
        
        {repository_data['name']}
        Language: {repository_data.get('language', 'Unknown')}
        
        {structure}
        
        Document:
        1. High-level architecture
        2. Component relationships
        3. Data flow
        4. Key design decisions
        5. Scalability considerations
        
        Format as markdown with clear sections.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a software architect documenting system design."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    async def _analyze_code_patterns(self, repository_data: Dict[str, any]) -> str:
        """Analyze code patterns for FAQ generation"""
        files = repository_data.get('files', [])
        
        # Look for common patterns
        patterns = {
            'has_tests': any('test' in f['path'].lower() for f in files),
            'has_config': any(any(c in f['path'].lower() for c in ['config', '.env', 'settings']) for f in files),
            'has_database': any(any(db in f['path'].lower() for db in ['model', 'schema', 'migration']) for f in files),
            'has_api': any(any(api in f['path'].lower() for api in ['api', 'route', 'endpoint']) for f in files),
            'has_frontend': any(f['language'] in ['javascript', 'typescript', 'html', 'css'] for f in files),
            'has_docker': any('docker' in f['path'].lower() for f in files)
        }
        
        return f"Code patterns detected: {patterns}"
