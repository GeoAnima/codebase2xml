"""Core XML generation functionality for codebase archiving."""

import os
import re
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
import xml.etree.ElementTree as ET
from xml.dom import minidom


class FileTypeDetector:
    """Detects file types and categorizes them."""
    
    PROGRAMMING_EXTENSIONS = {
        '.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.java': 'java',
        '.cpp': 'cpp', '.c': 'c', '.h': 'header', '.hpp': 'header',
        '.cs': 'csharp', '.php': 'php', '.rb': 'ruby', '.go': 'go',
        '.rs': 'rust', '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala',
        '.r': 'r', '.m': 'matlab', '.sh': 'shell', '.bash': 'shell',
        '.zsh': 'shell', '.fish': 'shell', '.ps1': 'powershell',
        '.sql': 'sql', '.pl': 'perl', '.lua': 'lua', '.dart': 'dart',
        '.elm': 'elm', '.ex': 'elixir', '.exs': 'elixir', '.clj': 'clojure',
        '.hs': 'haskell', '.ml': 'ocaml', '.fs': 'fsharp', '.vb': 'vbasic'
    }
    
    CONFIG_EXTENSIONS = {
        '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml', '.toml': 'toml',
        '.ini': 'ini', '.cfg': 'config', '.conf': 'config', '.properties': 'properties',
        '.env': 'environment', '.dockerignore': 'docker', '.gitignore': 'git',
        '.gitattributes': 'git', '.editorconfig': 'editor'
    }
    
    DOCUMENTATION_EXTENSIONS = {
        '.md': 'markdown', '.rst': 'restructuredtext', '.txt': 'text',
        '.doc': 'word', '.docx': 'word', '.pdf': 'pdf', '.rtf': 'rtf',
        '.tex': 'latex', '.org': 'org-mode', '.wiki': 'wiki'
    }
    
    WEB_EXTENSIONS = {
        '.html': 'html', '.htm': 'html', '.xml': 'xml', '.xhtml': 'xhtml',
        '.css': 'css', '.scss': 'scss', '.sass': 'sass', '.less': 'less',
        '.vue': 'vue', '.jsx': 'jsx', '.tsx': 'tsx', '.svelte': 'svelte'
    }
    
    DATA_EXTENSIONS = {
        '.csv': 'csv', '.tsv': 'tsv', '.xlsx': 'excel', '.xls': 'excel',
        '.ods': 'spreadsheet', '.sqlite': 'sqlite', '.db': 'database',
        '.parquet': 'parquet', '.arrow': 'arrow', '.avro': 'avro'
    }
    
    MEDIA_EXTENSIONS = {
        '.png': 'image', '.jpg': 'image', '.jpeg': 'image', '.gif': 'image',
        '.svg': 'vector', '.ico': 'icon', '.bmp': 'image', '.tiff': 'image',
        '.mp4': 'video', '.avi': 'video', '.mov': 'video', '.wmv': 'video',
        '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio', '.ogg': 'audio'
    }
    
    SPECIAL_FILES = {
        'README': 'documentation', 'LICENSE': 'license', 'CHANGELOG': 'documentation',
        'CONTRIBUTING': 'documentation', 'INSTALL': 'documentation', 'MANIFEST': 'manifest',
        'Makefile': 'build', 'makefile': 'build', 'CMakeLists.txt': 'build',
        'Dockerfile': 'docker', 'docker-compose.yml': 'docker', 'docker-compose.yaml': 'docker',
        'requirements.txt': 'dependencies', 'package.json': 'dependencies', 
        'setup.py': 'setup', 'setup.cfg': 'setup', 'pyproject.toml': 'setup',
        'Cargo.toml': 'dependencies', 'pom.xml': 'dependencies', 'build.gradle': 'build',
        'package-lock.json': 'lockfile', 'yarn.lock': 'lockfile', 'Pipfile.lock': 'lockfile'
    }
    
    def detect_type(self, file_path: Path) -> str:
        """Detect the type of a file based on its name and extension."""
        filename = file_path.name
        suffix = file_path.suffix.lower()
        
        # Check special files first
        if filename in self.SPECIAL_FILES:
            return self.SPECIAL_FILES[filename]
        
        # Check by extension
        if suffix in self.PROGRAMMING_EXTENSIONS:
            return self.PROGRAMMING_EXTENSIONS[suffix]
        elif suffix in self.CONFIG_EXTENSIONS:
            return self.CONFIG_EXTENSIONS[suffix]
        elif suffix in self.DOCUMENTATION_EXTENSIONS:
            return self.DOCUMENTATION_EXTENSIONS[suffix]
        elif suffix in self.WEB_EXTENSIONS:
            return self.WEB_EXTENSIONS[suffix]
        elif suffix in self.DATA_EXTENSIONS:
            return self.DATA_EXTENSIONS[suffix]
        elif suffix in self.MEDIA_EXTENSIONS:
            return self.MEDIA_EXTENSIONS[suffix]
        
        # Try to use mimetypes as fallback
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if mime_type.startswith('text/'):
                return 'text'
            elif mime_type.startswith('image/'):
                return 'image'
            elif mime_type.startswith('audio/'):
                return 'audio'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('application/'):
                return 'binary'
        
        # Default fallback
        if suffix:
            return f'unknown{suffix}'
        return 'unknown'


class CodebaseArchiver:
    """Main class for archiving codebases to XML."""
    
    def __init__(self, 
                 ignore_patterns: Optional[List[str]] = None,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 include_binary: bool = False):
        """
        Initialize the archiver.
        
        Args:
            ignore_patterns: List of glob patterns to ignore
            max_file_size: Maximum file size to include content for (bytes)
            include_binary: Whether to include binary file content
        """
        self.file_detector = FileTypeDetector()
        self.ignore_patterns = ignore_patterns or [
            '*.pyc', '__pycache__', '.git', '.svn', '.hg', 
            'node_modules', '.DS_Store', '*.log', '*.tmp',
            '.venv', 'venv', '.env', '.idea', '.vscode'
        ]
        self.max_file_size = max_file_size
        self.include_binary = include_binary
        
    def _should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored based on patterns."""
        path_str = str(path)
        name = path.name
        
        for pattern in self.ignore_patterns:
            if pattern in path_str or self._match_pattern(name, pattern):
                return True
        return False
    
    def _match_pattern(self, name: str, pattern: str) -> bool:
        """Simple glob pattern matching."""
        if '*' in pattern:
            # Convert glob pattern to regex
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            return re.match(f'^{regex_pattern}$', name) is not None
        return name == pattern
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Determine if a file is text-based and should have content included."""
        if not self.include_binary:
            file_type = self.file_detector.detect_type(file_path)
            binary_types = {'image', 'audio', 'video', 'binary', 'excel', 'sqlite', 'database'}
            if any(bt in file_type for bt in binary_types):
                return False
        
        try:
            # Try to read a small portion as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.read(1024)
            return True
        except (UnicodeDecodeError, PermissionError, OSError):
            return False
    
    def _get_file_stats(self, file_path: Path) -> Dict:
        """Get file statistics and metadata."""
        try:
            stat = file_path.stat()
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'permissions': oct(stat.st_mode)[-3:]
            }
        except (OSError, PermissionError):
            return {}
    
    def _count_lines(self, content: str) -> int:
        """Count the number of lines in content."""
        return len(content.splitlines()) if content else 0
    
    def _clean_xml_content(self, content: str) -> str:
        """Clean content to be XML-safe by removing invalid characters."""
        if not content:
            return content
        
        # Remove characters that are invalid in XML 1.0
        # Valid: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
        valid_chars = []
        for char in content:
            code = ord(char)
            if (code == 0x09 or code == 0x0A or code == 0x0D or 
                (0x20 <= code <= 0xD7FF) or 
                (0xE000 <= code <= 0xFFFD) or 
                (0x10000 <= code <= 0x10FFFF)):
                valid_chars.append(char)
            else:
                # Replace invalid characters with placeholder
                valid_chars.append('�')
        
        return ''.join(valid_chars)
    
    def _extract_metadata(self, codebase_path: Path) -> Dict:
        """Extract metadata about the codebase."""
        metadata = {
            'name': codebase_path.name,
            'path': str(codebase_path.absolute()),
            'timestamp': datetime.now().isoformat(),
            'total_files': 0,
            'total_directories': 0,
            'total_size': 0,
            'file_types': {},
            'languages': set()
        }
        
        for item in codebase_path.rglob('*'):
            if self._should_ignore(item):
                continue
                
            if item.is_file():
                metadata['total_files'] += 1
                try:
                    size = item.stat().st_size
                    metadata['total_size'] += size
                    
                    file_type = self.file_detector.detect_type(item)
                    metadata['file_types'][file_type] = metadata['file_types'].get(file_type, 0) + 1
                    
                    # Track programming languages
                    if file_type in self.file_detector.PROGRAMMING_EXTENSIONS.values():
                        metadata['languages'].add(file_type)
                        
                except (OSError, PermissionError):
                    pass
            elif item.is_dir():
                metadata['total_directories'] += 1
        
        metadata['languages'] = list(metadata['languages'])
        return metadata
    
    def _build_structure_tree(self, root_path: Path, current_path: Path) -> ET.Element:
        """Build the directory structure tree recursively."""
        rel_path = current_path.relative_to(root_path)
        
        if current_path.is_file():
            file_elem = ET.Element('file')
            file_elem.set('name', current_path.name)
            file_elem.set('type', self.file_detector.detect_type(current_path))
            return file_elem
        else:
            dir_elem = ET.Element('directory')
            dir_elem.set('name', current_path.name if current_path != root_path else '/')
            dir_elem.set('path', str(current_path))
            
            # Add children
            try:
                children = sorted(current_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                for child in children:
                    if not self._should_ignore(child):
                        child_elem = self._build_structure_tree(root_path, child)
                        dir_elem.append(child_elem)
            except (PermissionError, OSError):
                pass
                
            return dir_elem
    
    def archive_codebase(self, codebase_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Archive a codebase directory to XML format.
        
        Args:
            codebase_path: Path to the codebase directory
            output_path: Optional output path for the XML file
            
        Returns:
            Path to the generated XML file
        """
        if not codebase_path.exists():
            raise FileNotFoundError(f"Codebase path does not exist: {codebase_path}")
        
        if not codebase_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {codebase_path}")
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = codebase_path / f"{codebase_path.name}_archive_{timestamp}.xml"
        
        # Extract metadata
        metadata = self._extract_metadata(codebase_path)
        
        # Create root XML element
        root = ET.Element('codebase')
        root.set('name', metadata['name'])
        root.set('version', '1.0')
        root.set('timestamp', metadata['timestamp'])
        
        # Add metadata section
        meta_elem = ET.SubElement(root, 'metadata')
        
        desc_elem = ET.SubElement(meta_elem, 'description')
        desc_elem.text = f"Archived codebase: {metadata['name']}"
        
        path_elem = ET.SubElement(meta_elem, 'source_path')
        path_elem.text = metadata['path']
        
        stats_elem = ET.SubElement(meta_elem, 'statistics')
        stats_elem.set('total_files', str(metadata['total_files']))
        stats_elem.set('total_directories', str(metadata['total_directories']))
        stats_elem.set('total_size', str(metadata['total_size']))
        
        # Add file types
        if metadata['file_types']:
            types_elem = ET.SubElement(meta_elem, 'file_types')
            for file_type, count in sorted(metadata['file_types'].items()):
                type_elem = ET.SubElement(types_elem, 'type')
                type_elem.set('name', file_type)
                type_elem.set('count', str(count))
        
        # Add languages
        if metadata['languages']:
            langs_elem = ET.SubElement(meta_elem, 'languages')
            for lang in sorted(metadata['languages']):
                lang_elem = ET.SubElement(langs_elem, 'language')
                lang_elem.text = lang
        
        # Add structure section
        structure_elem = ET.SubElement(root, 'structure')
        structure_tree = self._build_structure_tree(codebase_path, codebase_path)
        structure_elem.append(structure_tree)
        
        # Add files section with content
        files_elem = ET.SubElement(root, 'files')
        
        for file_path in codebase_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore(file_path):
                try:
                    file_elem = ET.SubElement(files_elem, 'file')
                    file_elem.set('name', file_path.name)
                    file_elem.set('path', str(file_path))
                    file_elem.set('type', self.file_detector.detect_type(file_path))
                    
                    # Add file stats
                    stats = self._get_file_stats(file_path)
                    for key, value in stats.items():
                        file_elem.set(key, str(value))
                    
                    # Add content if it's a text file and not too large
                    if (file_path.stat().st_size <= self.max_file_size and 
                        self._is_text_file(file_path)):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                            if content.strip():  # Only add non-empty content
                                file_elem.set('lines', str(self._count_lines(content)))
                                content_elem = ET.SubElement(file_elem, 'content')
                                # Clean content for XML - remove invalid XML characters
                                clean_content = self._clean_xml_content(content)
                                content_elem.text = clean_content
                        except (UnicodeDecodeError, PermissionError, OSError):
                            # Add note about unreadable file
                            note_elem = ET.SubElement(file_elem, 'note')
                            note_elem.text = "Content could not be read"
                    else:
                        # Add note about why content was skipped
                        note_elem = ET.SubElement(file_elem, 'note')
                        if file_path.stat().st_size > self.max_file_size:
                            note_elem.text = f"File too large ({file_path.stat().st_size} bytes)"
                        else:
                            note_elem.text = "Binary file - content skipped"
                            
                except (OSError, PermissionError) as e:
                    # Add entry for inaccessible file
                    file_elem = ET.SubElement(files_elem, 'file')
                    file_elem.set('name', file_path.name)
                    file_elem.set('path', str(file_path))
                    file_elem.set('type', 'inaccessible')
                    note_elem = ET.SubElement(file_elem, 'note')
                    note_elem.text = f"Access denied: {str(e)}"
        
        # Write XML with pretty formatting
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ')
        
        # Remove empty lines from pretty printing
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        final_xml = '\n'.join(lines)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_xml)
        
        return output_path