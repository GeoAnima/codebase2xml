# codebase2xml

Transform any codebase directory into a comprehensive XML archive that preserves structure, content, and metadata.

## Overview

`codebase2xml` is a Python utility that creates lossless XML archives of codebases. It captures the complete directory structure, file contents, metadata, and provides intelligent file type detection. Perfect for:

- **AI & LLM workflows**
- **Codebase documentation and archival**
- **Project structure analysis** 
- **Backup and migration purposes**
- **Code review and analysis workflows**
- **Legal compliance and audit trails**

## Features

### 🏗️ Complete Structure Preservation
- Recursive directory tree capture
- File and folder hierarchy maintenance
- Symbolic link detection and handling

### 📄 Intelligent Content Handling
- Automatic text vs binary file detection
- Configurable file size limits
- Encoding-aware text processing
- Binary file metadata without content bloat

### 🔍 Advanced File Type Detection
- 50+ programming languages supported
- Configuration files (JSON, YAML, TOML, etc.)
- Documentation formats (Markdown, RST, etc.)
- Web technologies (HTML, CSS, JS frameworks)
- Data formats (CSV, Excel, databases)
- Media files (images, audio, video)
- Special files (README, LICENSE, Dockerfile, etc.)

### ⚙️ Flexible Configuration
- Customizable ignore patterns
- File size limits
- Binary content inclusion options
- Quiet mode for scripting

### 📊 Rich Metadata
- File statistics (size, dates, permissions)
- Language distribution analysis
- File type categorization
- Project-level metrics

## Installation

### From Source

```bash
git clone <repository-url>
cd codebase2xml
pip install -e .
```

### Requirements

- Python 3.8 or higher
- No external dependencies (uses only Python standard library)

## Usage

### Command Line Interface

#### Basic Usage

```bash
# Archive current directory
codebase2xml .

# Archive specific directory
codebase2xml /path/to/project

# Specify output location
codebase2xml /path/to/project --output /path/to/archive.xml
```

#### Advanced Options

```bash
# Custom ignore patterns
codebase2xml . --ignore "*.log,temp,node_modules,*.pyc"

# Set maximum file size (10MB default)
codebase2xml . --max-size 5242880  # 5MB

# Include binary file content (not recommended for large projects)
codebase2xml . --include-binary

# Quiet mode (only outputs result path)
codebase2xml . --quiet
```

### Python API

```python
from pathlib import Path
from codebase2xml import CodebaseArchiver

# Create archiver with custom settings
archiver = CodebaseArchiver(
    ignore_patterns=['*.log', 'node_modules', '.git'],
    max_file_size=10 * 1024 * 1024,  # 10MB
    include_binary=False
)

# Archive a codebase
codebase_path = Path('/path/to/project')
output_path = archiver.archive_codebase(codebase_path)

print(f"Archive created: {output_path}")
```

## Output Format

The generated XML follows this structure:

```xml
<?xml version="1.0" ?>
<codebase name="project-name" version="1.0" timestamp="2024-01-01T12:00:00">
  
  <!-- Project metadata -->
  <metadata>
    <description>Archived codebase: project-name</description>
    <source_path>/path/to/project</source_path>
    <statistics total_files="150" total_directories="25" total_size="2048576"/>
    
    <file_types>
      <type name="python" count="45"/>
      <type name="javascript" count="23"/>
      <type name="markdown" count="8"/>
      <!-- ... more types -->
    </file_types>
    
    <languages>
      <language>python</language>
      <language>javascript</language>
      <!-- ... more languages -->
    </languages>
  </metadata>

  <!-- Directory structure tree -->
  <structure>
    <directory name="/" path="/path/to/project">
      <file name="README.md" type="markdown"/>
      <file name="setup.py" type="setup"/>
      <directory name="src" path="/path/to/project/src">
        <!-- ... nested structure -->
      </directory>
    </directory>
  </structure>

  <!-- File contents and metadata -->
  <files>
    <file name="README.md" path="/path/to/project/README.md" 
          type="markdown" size="1024" lines="45" 
          modified="2024-01-01T12:00:00" permissions="644">
      <content><![CDATA[
        # Project Name
        Project description...
      ]]></content>
    </file>
    <!-- ... more files -->
  </files>

</codebase>
```

## File Type Detection

The system automatically detects and categorizes files:

### Programming Languages
Python, JavaScript, TypeScript, Java, C/C++, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, Scala, R, MATLAB, Shell scripts, PowerShell, SQL, Perl, Lua, Dart, Elm, Elixir, Clojure, Haskell, OCaml, F#, Visual Basic

### Configuration Files
JSON, YAML, TOML, INI, .env files, Docker configs, Git configs, Editor configs

### Documentation
Markdown, reStructuredText, plain text, Word docs, PDFs, LaTeX, Org-mode

### Web Technologies
HTML, CSS, SCSS/Sass, Less, Vue, JSX, TSX, Svelte

### Data Formats
CSV, TSV, Excel, SQLite, Parquet, Avro

### Special Files
README, LICENSE, CHANGELOG, Makefile, Dockerfile, package.json, requirements.txt, setup.py, and many more

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output XML file path | Auto-generated |
| `--ignore` | `-i` | Comma-separated ignore patterns | Common patterns |
| `--max-size` | `-s` | Maximum file size for content (bytes) | 10MB |
| `--include-binary` | `-b` | Include binary file content | False |
| `--quiet` | `-q` | Suppress progress output | False |
| `--version` | `-v` | Show version information | - |

## Default Ignore Patterns

The following patterns are ignored by default:

- `*.pyc`, `__pycache__` (Python cache)
- `.git`, `.svn`, `.hg` (Version control)
- `node_modules` (Node.js dependencies)
- `.DS_Store` (macOS metadata)
- `*.log`, `*.tmp` (Temporary files)
- `.venv`, `venv` (Virtual environments)
- `.env` (Environment files)
- `.idea`, `.vscode` (IDE files)

## Examples

### Archive a Python Project

```bash
codebase2xml my-python-project --ignore "*.pyc,__pycache__,.pytest_cache,dist,build"
```

### Archive a Node.js Project

```bash
codebase2xml my-node-app --ignore "node_modules,dist,build,.next,.nuxt"
```

### Archive with Custom Settings

```bash
codebase2xml . \
  --output detailed_archive.xml \
  --max-size 20971520 \
  --ignore "*.log,temp,cache" \
  --include-binary
```

### Scripting Integration

```bash
# Generate archive and capture output path
ARCHIVE_PATH=$(codebase2xml . --quiet)
echo "Archive created at: $ARCHIVE_PATH"

# Upload to cloud storage, send via email, etc.
aws s3 cp "$ARCHIVE_PATH" s3://my-bucket/archives/
```

## Use Cases

### 📚 Documentation
Create comprehensive project documentation that includes both structure and content for onboarding or handoffs.

### 🔒 Compliance
Generate audit trails and compliance documentation for regulated industries.

### 🏗️ Migration
Prepare codebases for migration between systems while preserving complete context.

### 🔍 Analysis
Enable detailed code analysis, dependency tracking, and architectural reviews.

### 💾 Backup
Create structured backups that are more useful than simple file copies.

### 🤖 AI/ML Training
Prepare codebases for AI model training with structured, labeled data.

## Technical Details

### Performance
- Handles large codebases efficiently
- Memory-conscious streaming for large files
- Parallel processing where possible
- Configurable limits to prevent resource exhaustion

### Compatibility
- Cross-platform (Windows, macOS, Linux)
- Python 3.8+ support
- No external dependencies
- Unicode and encoding-aware

### Security
- No network operations
- Read-only filesystem access
- Configurable file size limits
- Safe handling of binary content