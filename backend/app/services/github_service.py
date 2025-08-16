import git
import os
import shutil
import tempfile
import asyncio
from typing import List, Dict, Optional, Tuple
from github import Github, GithubException
import aiofiles
from pathlib import Path
import logging

from app.core.config import settings
from app.services.content_filter import ContentFilter

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.github = Github(settings.GITHUB_TOKEN) if settings.GITHUB_TOKEN else None
        self.content_filter = ContentFilter()
        
    async def validate_repository(self, repo_url: str) -> Dict[str, any]:
        """Validate and extract repository information"""
        try:
            # Parse GitHub URL
            repo_path = self._parse_github_url(repo_url)
            if not repo_path:
                raise ValueError("Invalid GitHub repository URL")
            
            # Get repository metadata
            if self.github:
                repo = self.github.get_repo(repo_path)
                return {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.clone_url,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "size": repo.size,
                    "default_branch": repo.default_branch
                }
            else:
                # Basic validation without API
                return {
                    "name": repo_path.split("/")[-1],
                    "full_name": repo_path,
                    "url": f"https://github.com/{repo_path}.git",
                    "description": None,
                    "language": None,
                    "stars": 0,
                    "forks": 0,
                    "size": 0,
                    "default_branch": "main"
                }
                
        except GithubException as e:
            logger.error(f"GitHub API error: {str(e)}")
            raise ValueError(f"Repository not accessible: {str(e)}")
        except Exception as e:
            logger.error(f"Repository validation error: {str(e)}")
            raise ValueError(f"Invalid repository: {str(e)}")
    
    async def clone_repository(self, repo_url: str, temp_dir: str) -> str:
        """Clone repository to temporary directory"""
        try:
            logger.info(f"Cloning repository: {repo_url}")
            
            # Use asyncio to run git clone in thread pool
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: git.Repo.clone_from(
                    repo_url, 
                    temp_dir,
                    depth=1  # Shallow clone for efficiency
                )
            )
            
            logger.info(f"Repository cloned to: {temp_dir}")
            return temp_dir
            
        except git.exc.GitCommandError as e:
            logger.error(f"Git clone error: {str(e)}")
            raise ValueError(f"Failed to clone repository: {str(e)}")
        except Exception as e:
            logger.error(f"Clone error: {str(e)}")
            raise ValueError(f"Repository clone failed: {str(e)}")
    
    async def process_repository(self, repo_path: str) -> List[Dict[str, any]]:
        """Process repository files and extract content"""
        try:
            logger.info(f"Processing repository at: {repo_path}")
            
            files_data = []
            total_size = 0
            
            for root, dirs, files in os.walk(repo_path):
                # Filter directories
                dirs[:] = [d for d in dirs if not self.content_filter.should_ignore_directory(d)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    # Check if file should be processed
                    if not self.content_filter.should_process_file(file_path):
                        continue
                    
                    # Check file size
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > settings.MAX_FILE_SIZE:
                            logger.warning(f"Skipping large file: {relative_path} ({file_size} bytes)")
                            continue
                        
                        total_size += file_size
                        if total_size > settings.MAX_REPO_SIZE:
                            logger.warning("Repository size limit exceeded")
                            break
                        
                        # Read file content
                        content = await self._read_file_content(file_path)
                        if content and not self.content_filter.contains_secrets(content):
                            files_data.append({
                                "path": relative_path,
                                "content": content,
                                "language": self._detect_language(file_path),
                                "size": file_size
                            })
                    
                    except Exception as e:
                        logger.warning(f"Error processing file {relative_path}: {str(e)}")
                        continue
                
                if total_size > settings.MAX_REPO_SIZE:
                    break
            
            logger.info(f"Processed {len(files_data)} files, total size: {total_size} bytes")
            return files_data
            
        except Exception as e:
            logger.error(f"Repository processing error: {str(e)}")
            raise ValueError(f"Failed to process repository: {str(e)}")
    
    async def _read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content with encoding detection"""
        try:
            # Try UTF-8 first
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except UnicodeDecodeError:
            try:
                # Try latin-1 as fallback
                async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
                    return await f.read()
            except Exception:
                logger.warning(f"Could not read file: {file_path}")
                return None
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {str(e)}")
            return None
    
    def _parse_github_url(self, url: str) -> Optional[str]:
        """Extract owner/repo from GitHub URL"""
        try:
            # Handle different URL formats
            if url.startswith('https://github.com/'):
                path = url.replace('https://github.com/', '').rstrip('.git')
            elif url.startswith('git@github.com:'):
                path = url.replace('git@github.com:', '').rstrip('.git')
            else:
                # Assume it's already in owner/repo format
                path = url.strip('/')
            
            # Validate format
            parts = path.split('/')
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
            
            return None
        except Exception:
            return None
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.sh': 'bash',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.md': 'markdown',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'ini',
            '.conf': 'ini'
        }
        
        return language_map.get(ext, 'text')
