import re
import os
from pathlib import Path
from typing import Set, List, Pattern
import logging

logger = logging.getLogger(__name__)

class ContentFilter:
    def __init__(self):
        self.ignored_dirs = {
            '.git', '.svn', '.hg', '.bzr',
            'node_modules', '__pycache__', '.pytest_cache',
            'venv', 'env', '.venv', '.env',
            'dist', 'build', 'target', 'out',
            '.idea', '.vscode', '.vs',
            'coverage', '.coverage', '.nyc_output',
            'logs', 'log', 'tmp', 'temp',
            '.DS_Store', 'Thumbs.db',
            'bower_components', 'vendor'
        }
        
        self.ignored_extensions = {
            # Binaries and executables
            '.exe', '.dll', '.so', '.dylib', '.app',
            '.bin', '.deb', '.rpm', '.msi', '.dmg',
            
            # Images and media
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg',
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
            '.mp3', '.wav', '.ogg', '.flac', '.aac',
            
            # Archives
            '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
            
            # Documents
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            
            # Fonts
            '.ttf', '.otf', '.woff', '.woff2', '.eot',
            
            # Other
            '.ico', '.cur', '.db', '.sqlite', '.lock'
        }
        
        self.processable_extensions = {
            # Code files
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs',
            '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.clj',
            '.sh', '.ps1', '.sql',
            
            # Web files
            '.html', '.css', '.scss', '.less',
            
            # Config and data
            '.json', '.xml', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf',
            
            # Documentation
            '.md', '.rst', '.txt',
            
            # Makefiles and scripts
            'Makefile', 'Dockerfile', '.dockerfile',
        }
        
        # Secret detection patterns
        self.secret_patterns: List[Pattern] = [
            # API keys
            re.compile(r'api[_\-]?key\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', re.IGNORECASE),
            re.compile(r'secret[_\-]?key\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', re.IGNORECASE),
            re.compile(r'access[_\-]?token\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', re.IGNORECASE),
            
            # AWS keys
            re.compile(r'AKIA[0-9A-Z]{16}', re.IGNORECASE),
            re.compile(r'aws[_\-]?secret[_\-]?access[_\-]?key', re.IGNORECASE),
            
            # GitHub tokens
            re.compile(r'ghp_[a-zA-Z0-9]{36}'),
            re.compile(r'github[_\-]?token', re.IGNORECASE),
            
            # Other common patterns
            re.compile(r'password\s*[=:]\s*["\']([^"\']{8,})["\']', re.IGNORECASE),
            re.compile(r'bearer\s+[a-zA-Z0-9_\-\.]{20,}', re.IGNORECASE),
            re.compile(r'sk_[a-z]{2,20}_[a-zA-Z0-9]{20,}'),  # Stripe keys
            
            # Connection strings
            re.compile(r'mongodb://[^/\s]+:[^@\s]+@', re.IGNORECASE),
            re.compile(r'postgres://[^/\s]+:[^@\s]+@', re.IGNORECASE),
            re.compile(r'mysql://[^/\s]+:[^@\s]+@', re.IGNORECASE),
        ]
    
    def should_ignore_directory(self, dirname: str) -> bool:
        """Check if directory should be ignored"""
        return dirname in self.ignored_dirs or dirname.startswith('.')
    
    def should_process_file(self, filepath: str) -> bool:
        """Check if file should be processed"""
        path = Path(filepath)
        
        # Check if it's a file
        if not path.is_file():
            return False
        
        # Check file size (basic check)
        try:
            if path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                return False
        except OSError:
            return False
        
        # Check extension
        ext = path.suffix.lower()
        filename = path.name.lower()
        
        # Always ignore certain extensions
        if ext in self.ignored_extensions:
            return False
        
        # Process known good extensions
        if ext in self.processable_extensions:
            return True
        
        # Process files with no extension that might be important
        if not ext and filename in {'dockerfile', 'makefile', 'rakefile', 'gemfile'}:
            return True
        
        # Process README and LICENSE files
        if filename.startswith(('readme', 'license', 'changelog', 'contributing')):
            return True
        
        return False
    
    def contains_secrets(self, content: str) -> bool:
        """Check if content contains potential secrets"""
        try:
            for pattern in self.secret_patterns:
                if pattern.search(content):
                    logger.warning("Potential secret detected in content")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking for secrets: {str(e)}")
            return False
    
    def sanitize_content(self, content: str) -> str:
        """Remove or mask potential secrets from content"""
        try:
            sanitized = content
            for pattern in self.secret_patterns:
                sanitized = pattern.sub('***REDACTED***', sanitized)
            return sanitized
        except Exception as e:
            logger.error(f"Error sanitizing content: {str(e)}")
            return content
