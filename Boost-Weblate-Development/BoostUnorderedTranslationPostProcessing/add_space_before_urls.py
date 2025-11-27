#!/usr/bin/env python3
"""
Script to insert a space before all http:// and https:// URLs in *_zh_Hans.adoc files
if they don't already have whitespace before them.
"""

import re
import os
from pathlib import Path


def add_space_before_urls(content: str) -> tuple[str, int]:
    """
    Add space before all http:// and https:// URLs that don't have whitespace before them.
    Returns (modified_content, number_of_replacements)
    
    URLs can have optional bracket content like: https://url[text]
    The bracket content can span multiple lines.
    All matched URLs will have a space inserted before them if needed.
    """
    # Pattern to match a complete URL including optional bracket content
    # URL part: https?://[^\s\[\]]+
    # Optional bracket content: \[.*?\] (multi-line, non-greedy with DOTALL)
    url_pattern = r'https?://[^\s\[\]]+(?:\[.*?\])?'
    
    # Comprehensive pattern to match all URLs in any context
    # Pattern 1: URLs at start of string or after newline (with optional whitespace)
    # Pattern 2: URLs after non-whitespace characters
    # We'll match both cases and ensure all URLs have a space before them
    
    total_count = 0
    
    # Pattern 1: Match URLs at start of line or string
    pattern1 = rf'(^|\n)(\s*)({url_pattern})'
    
    def replace_func1(match):
        prefix = match.group(1)  # ^ or \n
        existing_whitespace = match.group(2)  # Any existing whitespace
        url = match.group(3)  # The URL
        
        # Skip if it's part of a link: macro
        if prefix == '\n':
            start_pos = match.start()
            if start_pos > 0:
                prev_newline = content.rfind('\n', 0, start_pos - 1)
                if prev_newline >= 0:
                    prev_line = content[prev_newline + 1:start_pos - 1]
                    if prev_line.rstrip().endswith('link:'):
                        return match.group(0)  # Don't modify link: macros
        
        # If there's already a space or tab, don't add another
        if existing_whitespace and any(c in existing_whitespace for c in ' \t'):
            return match.group(0)  # Don't modify
        
        # Add space after prefix and any existing newlines
        return f"{prefix}{existing_whitespace} {url}"
    
    content, count1 = re.subn(pattern1, replace_func1, content, flags=re.MULTILINE | re.DOTALL)
    total_count += count1
    
    # Pattern 2: Match URLs after non-whitespace characters (figures, numbers, symbols, etc.)
    # Match one or more non-whitespace characters to handle cases like "图1https://..." or "123https://..."
    pattern2 = rf'([^\s]+)({url_pattern})'
    
    def replace_func2(match):
        chars_before = match.group(1)  # One or more non-whitespace characters
        url = match.group(2)  # The URL
        
        # Skip if it's part of a link: macro (chars_before ends with 'link:')
        if chars_before.endswith('link:'):
            return match.group(0)  # Don't modify link: macros
        
        # Add space after the characters (handles figures, numbers, symbols, text, etc.)
        return f"{chars_before} {url}"
    
    content, count2 = re.subn(pattern2, replace_func2, content)
    total_count += count2
    
    return content, total_count


def process_file(filepath: str, dry_run: bool = False) -> int:
    """Process a single *_zh_Hans.adoc file and add spaces before URLs"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=os.sys.stderr)
        return 0
    
    modified_content, count = add_space_before_urls(content)
    
    if count > 0:
        if dry_run:
            print(f"Would modify {filepath}: {count} URL(s) need space")
        else:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                print(f"Modified {filepath}: added space before {count} URL(s)")
            except Exception as e:
                print(f"Error writing {filepath}: {e}", file=os.sys.stderr)
                return 0
    
    return count


def find_zh_hans_adoc_files(doc_dir: str) -> list[str]:
    """Recursively find all *_zh_Hans.adoc files in the doc directory"""
    adoc_files = []
    doc_path = Path(doc_dir)
    
    if not doc_path.exists():
        print(f"Error: Directory {doc_dir} does not exist", file=os.sys.stderr)
        return []
    
    for file_path in doc_path.rglob('*_zh_Hans.adoc'):
        adoc_files.append(str(file_path))
    
    return sorted(adoc_files)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Insert space before http:// and https:// URLs in *_zh_Hans.adoc files'
    )
    parser.add_argument(
        '--doc-dir',
        default='doc',
        help='Directory containing *_zh_Hans.adoc files (default: doc)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    
    args = parser.parse_args()
    
    # Find all *_zh_Hans.adoc files
    adoc_files = find_zh_hans_adoc_files(args.doc_dir)
    
    if not adoc_files:
        print(f"No *_zh_Hans.adoc files found in {args.doc_dir}")
        return
    
    print(f"Processing {len(adoc_files)} *_zh_Hans.adoc files...")
    if args.dry_run:
        print("DRY RUN MODE - no files will be modified\n")
    
    total_replacements = 0
    files_modified = 0
    
    for filepath in adoc_files:
        count = process_file(filepath, dry_run=args.dry_run)
        if count > 0:
            files_modified += 1
            total_replacements += count
    
    print(f"\n{'Would modify' if args.dry_run else 'Modified'} {files_modified} file(s)")
    print(f"Total replacements: {total_replacements}")


if __name__ == '__main__':
    main()

