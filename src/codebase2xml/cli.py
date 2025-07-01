"""Command-line interface for codebase2xml."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .core import CodebaseArchiver


def parse_ignore_patterns(patterns_str: str) -> List[str]:
    """Parse comma-separated ignore patterns."""
    if not patterns_str:
        return []
    return [pattern.strip() for pattern in patterns_str.split(',') if pattern.strip()]


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    """Main entry point for the codebase2xml CLI."""
    parser = argparse.ArgumentParser(
        prog='codebase2xml',
        description='Transform any codebase directory into a comprehensive XML archive',
        epilog='Example: codebase2xml /path/to/project --output project_archive.xml'
    )
    
    # Positional argument
    parser.add_argument(
        'codebase_path',
        type=str,
        help='Path to the codebase directory to archive'
    )
    
    # Optional arguments
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output XML file path (default: generated in codebase directory)'
    )
    
    parser.add_argument(
        '--ignore', '-i',
        type=str,
        default='',
        help='Comma-separated list of patterns to ignore (e.g., "*.log,temp,*.tmp")'
    )
    
    parser.add_argument(
        '--max-size', '-s',
        type=int,
        default=10 * 1024 * 1024,  # 10MB
        help='Maximum file size to include content for (bytes, default: 10MB)'
    )
    
    parser.add_argument(
        '--include-binary', '-b',
        action='store_true',
        help='Include binary file content (not recommended for large files)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    codebase_path = Path(args.codebase_path).resolve()
    if not codebase_path.exists():
        print(f"❌ Error: Codebase path does not exist: {codebase_path}", file=sys.stderr)
        sys.exit(1)
    
    if not codebase_path.is_dir():
        print(f"❌ Error: Path is not a directory: {codebase_path}", file=sys.stderr)
        sys.exit(1)
    
    # Parse output path
    output_path = None
    if args.output:
        output_path = Path(args.output).resolve()
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Parse ignore patterns
    ignore_patterns = parse_ignore_patterns(args.ignore)
    
    try:
        if not args.quiet:
            print(f"🔍 Analyzing codebase: {codebase_path}")
            if ignore_patterns:
                print(f"   Ignoring patterns: {', '.join(ignore_patterns)}")
            print(f"   Max file size: {format_size(args.max_size)}")
            print(f"   Include binary: {'Yes' if args.include_binary else 'No'}")
            print()
        
        # Create archiver
        archiver = CodebaseArchiver(
            ignore_patterns=ignore_patterns,
            max_file_size=args.max_size,
            include_binary=args.include_binary
        )
        
        # Generate archive
        if not args.quiet:
            print("📦 Generating XML archive...")
        
        result_path = archiver.archive_codebase(codebase_path, output_path)
        
        if not args.quiet:
            # Show results
            archive_size = result_path.stat().st_size
            print(f"\n✅ Archive created successfully!")
            print(f"   Output file: {result_path}")
            print(f"   Archive size: {format_size(archive_size)}")
            print(f"\n📊 Archive contains:")
            
            # Quick stats from the archiver's last run
            print(f"   📁 Directories: {archiver._extract_metadata(codebase_path)['total_directories']}")
            print(f"   📄 Files: {archiver._extract_metadata(codebase_path)['total_files']}")
            print(f"   💾 Total size: {format_size(archiver._extract_metadata(codebase_path)['total_size'])}")
        else:
            # Just print the output path for scripts
            print(str(result_path))
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Archive generation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except PermissionError as e:
        print(f"❌ Permission denied: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"❌ System error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()