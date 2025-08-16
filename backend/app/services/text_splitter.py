import re
from typing import List, Dict, Optional
import tree_sitter
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript
from pathlib import Path

from app.core.config import settings

class TextSplitter:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        
        # Initialize tree-sitter parsers
        self.parsers = {}
        self._setup_parsers()
    
    def _setup_parsers(self):
        """Setup tree-sitter parsers for different languages"""
        try:
            # Python parser
            python_language = tree_sitter.Language(tree_sitter_python.language(), "python")
            python_parser = tree_sitter.Parser()
            python_parser.set_language(python_language)
            self.parsers['python'] = python_parser
            
            # JavaScript parser
            js_language = tree_sitter.Language(tree_sitter_javascript.language(), "javascript")
            js_parser = tree_sitter.Parser()
            js_parser.set_language(js_language)
            self.parsers['javascript'] = js_parser
            
            # TypeScript parser
            ts_language = tree_sitter.Language(tree_sitter_typescript.language(), "typescript")
            ts_parser = tree_sitter.Parser()
            ts_parser.set_language(ts_language)
            self.parsers['typescript'] = ts_parser
            
        except Exception as e:
            print(f"Warning: Could not initialize tree-sitter parsers: {e}")
    
    async def split_code(self, content: str, language: str, file_path: str) -> List[Dict[str, any]]:
        """Split code content into meaningful chunks"""
        
        # Try AST-based splitting first
        if language in self.parsers:
            try:
                return await self._split_with_ast(content, language, file_path)
            except Exception as e:
                print(f"AST parsing failed for {file_path}, falling back to text splitting: {e}")
        
        # Fall back to text-based splitting
        return await self._split_by_text(content, language, file_path)
    
    async def _split_with_ast(self, content: str, language: str, file_path: str) -> List[Dict[str, any]]:
        """Split code using AST parsing"""
        parser = self.parsers[language]
        tree = parser.parse(bytes(content, 'utf-8'))
        
        chunks = []
        lines = content.split('\n')
        
        # Extract top-level constructs
        for node in tree.root_node.children:
            if node.type in ['function_definition', 'class_definition', 'method_definition']:
                start_line = node.start_point[0]
                end_line = node.end_point[0]
                
                # Get the content of this construct
                chunk_content = '\n'.join(lines[start_line:end_line + 1])
                
                chunks.append({
                    'content': chunk_content,
                    'type': node.type,
                    'start_line': start_line,
                    'end_line': end_line,
                    'language': language,
                    'file_path': file_path
                })
        
        # If no functions/classes found, split by text
        if not chunks:
            return await self._split_by_text(content, language, file_path)
        
        return chunks
    
    async def _split_by_text(self, content: str, language: str, file_path: str) -> List[Dict[str, any]]:
        """Split content by text-based rules"""
        
        # For markdown files, split by sections
        if language == 'markdown':
            return self._split_markdown(content, file_path)
        
        # For other files, use sliding window approach
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_size = 0
        
        for i, line in enumerate(lines):
            line_size = len(line)
            
            if current_size + line_size > self.chunk_size and current_chunk:
                # Create chunk
                chunk_content = '\n'.join(current_chunk)
                chunks.append({
                    'content': chunk_content,
                    'type': 'text_chunk',
                    'start_line': i - len(current_chunk),
                    'end_line': i - 1,
                    'language': language,
                    'file_path': file_path
                })
                
                # Start new chunk with overlap
                overlap_lines = max(1, len(current_chunk) * self.chunk_overlap // self.chunk_size)
                current_chunk = current_chunk[-overlap_lines:] if overlap_lines > 0 else []
                current_size = sum(len(l) for l in current_chunk)
            
            current_chunk.append(line)
            current_size += line_size
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append({
                'content': chunk_content,
                'type': 'text_chunk',
                'start_line': len(lines) - len(current_chunk),
                'end_line': len(lines) - 1,
                'language': language,
                'file_path': file_path
            })
        
        return chunks
    
    def _split_markdown(self, content: str, file_path: str) -> List[Dict[str, any]]:
        """Split markdown by sections"""
        chunks = []
        lines = content.split('\n')
        
        current_section = []
        current_title = "Introduction"
        start_line = 0
        
        for i, line in enumerate(lines):
            # Check for header
            if line.strip().startswith('#'):
                # Save previous section
                if current_section:
                    chunk_content = '\n'.join(current_section)
                    chunks.append({
                        'content': chunk_content,
                        'type': 'markdown_section',
                        'title': current_title,
                        'start_line': start_line,
                        'end_line': i - 1,
                        'language': 'markdown',
                        'file_path': file_path
                    })
                
                # Start new section
                current_title = line.strip('# ')
                current_section = [line]
                start_line = i
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            chunk_content = '\n'.join(current_section)
            chunks.append({
                'content': chunk_content,
                'type': 'markdown_section',
                'title': current_title,
                'start_line': start_line,
                'end_line': len(lines) - 1,
                'language': 'markdown',
                'file_path': file_path
            })
        
        return chunks
