#!/usr/bin/env python3
"""
Script to extract all links from *_zh_Hans.adoc files in the doc folder.
"""

import os
import re
import argparse
from pathlib import Path
from collections import defaultdict

def find_zh_hans_files(doc_dir):
    """Find all files matching *_zh_Hans.adoc in the doc directory."""
    doc_path = Path(doc_dir)
    if not doc_path.exists():
        print(f"Error: Directory {doc_dir} does not exist")
        return []
    
    files = list(doc_path.rglob("*_zh_Hans.adoc"))
    return sorted(files)

def transform_link_target(target, suffix, target_extension):
    """
    Transform a link target by adding a suffix and changing the extension.
    
    Args:
        target: The original link target (e.g., 'reference/unordered_map.html')
        suffix: Suffix to add before extension (e.g., '_zh_Hans')
        target_extension: New extension to use (e.g., '.adoc')
    
    Returns:
        Transformed target (e.g., 'reference/unordered_map_zh_Hans.adoc')
    """
    if not target:
        return target
    
    # Handle anchors (e.g., 'file.html#anchor')
    if '#' in target:
        base_target, anchor = target.rsplit('#', 1)
        transformed_base = transform_link_target(base_target, suffix, target_extension)
        return f"{transformed_base}#{anchor}"
    
    # Get the path without extension
    target_path = Path(target)
    stem = target_path.stem  # filename without extension
    parent = target_path.parent  # directory part
    
    # Add suffix and new extension
    new_name = f"{stem}{suffix}{target_extension}"
    
    # Reconstruct the path
    if parent == Path('.'):
        return str(new_name)
    else:
        return str(parent / new_name)

def replace_link_in_content(content, original_match, original_target, transformed_target, link_type):
    """
    Replace a link in the content with the transformed target.
    
    Args:
        content: The file content
        original_match: The original full match string (e.g., 'link:file.html[]')
        original_target: The original target (e.g., 'file.html')
        transformed_target: The transformed target (e.g., 'file_zh_Hans.adoc')
        link_type: Type of link ('link', 'xref', 'anchor', etc.)
    
    Returns:
        Content with the link replaced
    """
    if link_type == 'link':
        # link:target[] or link:target[text]
        # Extract the text part if it exists
        if '[' in original_match and ']' in original_match:
            # Has text: link:target[text]
            text_part = original_match[original_match.index('['):]
            new_match = f"link:{transformed_target}{text_part}"
        else:
            # No text: link:target[]
            new_match = f"link:{transformed_target}[]"
        return content.replace(original_match, new_match, 1)
    
    elif link_type == 'xref':
        # xref:target[] or xref:target[text]
        if '[' in original_match and ']' in original_match:
            text_part = original_match[original_match.index('['):]
            new_match = f"xref:{transformed_target}{text_part}"
        else:
            new_match = f"xref:{transformed_target}[]"
        return content.replace(original_match, new_match, 1)
    
    elif link_type == 'anchor':
        # <<target,text>> or <<target>>
        if ',' in original_match:
            # Has text: <<target,text>>
            text_part = original_match[original_match.index(','):original_match.rindex('>')]
            new_match = f"<<{transformed_target}{text_part}>>"
        else:
            # No text: <<target>>
            new_match = f"<<{transformed_target}>>"
        return content.replace(original_match, new_match, 1)
    
    elif link_type == 'image':
        # image:target[attributes] or link:target[image:target[attributes]]
        # This is more complex, handle the image: part inside link:
        if 'image:' in original_match:
            # Replace the target in the image: part
            new_match = original_match.replace(original_target, transformed_target, 1)
            return content.replace(original_match, new_match, 1)
        return content
    
    # For other types, just replace the target
    return content.replace(original_target, transformed_target, 1)

def is_link_in_root_folder(target, source_file, include_dir, exclude_except_dir=None, allowed_extensions=None):
    """
    Check if a link target points to a file inside the include_dir,
    excluding files in the exclude_except_dir, and matching allowed file extensions.
    
    Main logic: Check if the resolved link target is within include_dir's files,
    but exclude files that are within exclude_except_dir, and only include files
    with allowed extensions.
    
    Args:
        target: The link target (e.g., 'intro.adoc', 'reference/map.html')
        source_file: The file where the link was found (Path object)
        include_dir: The directory to include links from (Path object)
        exclude_except_dir: The directory to exclude from links (Path object, optional)
        allowed_extensions: List of allowed file extensions (e.g., ['.html', '.adoc']), optional
    
    Returns:
        True if the target resolves to a file path within include_dir (but not in exclude_except_dir)
        and matches allowed extensions, False otherwise
    """
    # Skip external URLs
    if target.startswith(('http://', 'https://', '//')):
        return False
    
    # Skip absolute paths (starting with /)
    if target.startswith('/'):
        return False
    
    # Skip anchor-only references (starting with #)
    if target.startswith('#'):
        return False
    
    # Skip mailto: and other protocols
    if ':' in target and not target.startswith('./') and not target.startswith('../'):
        # Check if it's a protocol (like mailto:, ftp:, etc.)
        protocol = target.split(':', 1)[0]
        if protocol.lower() not in ['link', 'xref', 'image']:
            return False
    
    # Main logic: Resolve the target path and check if it's within include_dir
    # (excluding exclude_except_dir if specified)
    source_dir = source_file.parent
    try:
        # Handle targets with anchors (e.g., 'file.html#anchor')
        target_path = target.split('#')[0]
        
        # Resolve relative to source file directory
        resolved_path = (source_dir / target_path).resolve()
        
        # Check if resolved path is within include_dir
        try:
            resolved_path.relative_to(include_dir.resolve())
            
            # Exclude paths within exclude_except_dir if specified
            if exclude_except_dir:
                try:
                    resolved_path.relative_to(exclude_except_dir.resolve())
                    # Path is within exclude_except_dir, exclude it
                    return False
                except ValueError:
                    # Path is not within exclude_except_dir, continue
                    pass
            
            # Check if file extension matches allowed extensions
            if allowed_extensions:
                file_ext = resolved_path.suffix.lower()
                if file_ext not in allowed_extensions:
                    # File extension doesn't match allowed extensions
                    return False
            
            # Link target is within include_dir, not in exclude_except_dir, and matches allowed extensions
            return True
        except ValueError:
            # Path is not within include_dir directory
            return False
    except Exception:
        # If we can't resolve the path, skip it
        return False

def extract_links(content, filepath):
    """Extract all links from AsciiDoc content."""
    links = []
    
    # Pattern 1: link:target[] or link:target[text]
    # Matches: link:target[] or link:target[text] or link:target[text with spaces]
    link_pattern = r'link:([^\s\[\]]+)(?:\[([^\]]*)\])?'
    for match in re.finditer(link_pattern, content):
        target = match.group(1)
        text = match.group(2) if match.group(2) else ""
        links.append({
            'type': 'link',
            'target': target,
            'text': text,
            'full_match': match.group(0),
            'file': str(filepath)
        })
    
    # Pattern 2: xref:target[text] or xref:target[]
    xref_pattern = r'xref:([^\s\[\]]+)(?:\[([^\]]*)\])?'
    for match in re.finditer(xref_pattern, content):
        target = match.group(1)
        text = match.group(2) if match.group(2) else ""
        links.append({
            'type': 'xref',
            'target': target,
            'text': text,
            'full_match': match.group(0),
            'file': str(filepath)
        })
    
    # Pattern 3: <<target,text>> or <<target>>
    anchor_pattern = r'<<([^,>]+)(?:,([^>]+))?>>'
    for match in re.finditer(anchor_pattern, content):
        target = match.group(1)
        text = match.group(2) if match.group(2) else ""
        links.append({
            'type': 'anchor',
            'target': target,
            'text': text,
            'full_match': match.group(0),
            'file': str(filepath)
        })
    
    # Pattern 4: URLs (http:// or https://)
    url_pattern = r'(https?://[^\s\[\]]+)(?:\[([^\]]+)\])?'
    for match in re.finditer(url_pattern, content):
        url = match.group(1)
        text = match.group(2) if match.group(2) else ""
        links.append({
            'type': 'url',
            'target': url,
            'text': text,
            'full_match': match.group(0),
            'file': str(filepath)
        })
    
    # Pattern 5: image:target[attributes] (images are also links)
    image_pattern = r'image:([^\s\[\]]+)(?:\[([^\]]*)\])?'
    for match in re.finditer(image_pattern, content):
        target = match.group(1)
        text = match.group(2) if match.group(2) else ""
        links.append({
            'type': 'image',
            'target': target,
            'text': text,
            'full_match': match.group(0),
            'file': str(filepath)
        })
    
    return links

def main():
    parser = argparse.ArgumentParser(
        description='Extract links from *_zh_Hans.adoc files in the doc folder'
    )
    parser.add_argument(
        '--doc-dir',
        type=str,
        default='doc',
        help='Directory to search for *_zh_Hans.adoc files (default: doc)'
    )
    parser.add_argument(
        '--include-dir',
        type=str,
        default='doc/modules/ROOT',
        help='Directory to include links from (default: doc/modules/ROOT)'
    )
    parser.add_argument(
        '--except-dir',
        type=str,
        default='doc/modules/ROOT/images',
        help='Directory to exclude from links (default: doc/modules/ROOT/images)'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        default='extracted_links.txt',
        help='Output file to write results to (default: extracted_links.txt)'
    )
    parser.add_argument(
        '--file-extensions',
        type=str,
        nargs='+',
        default=['.html'],
        help='File extensions to include (e.g., .html .adoc). Default: .html'
    )
    parser.add_argument(
        '--suffix',
        type=str,
        default='_zh_Hans',
        help='Suffix to add to link targets before extension (default: _zh_Hans)'
    )
    parser.add_argument(
        '--target-extension',
        type=str,
        default='.adoc',
        help='Target extension to change links to (default: .adoc)'
    )
    parser.add_argument(
        '--modify-files',
        action='store_true',
        help='Actually modify the source files with transformed links (default: False, only extract)'
    )
    
    args = parser.parse_args()
    
    doc_dir = args.doc_dir
    include_dir = args.include_dir
    except_dir = args.except_dir
    output_file = args.output_file
    # Normalize extensions to lowercase and ensure they start with a dot
    file_extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in args.file_extensions]
    suffix = args.suffix
    # Normalize target extension to ensure it starts with a dot
    target_extension = args.target_extension if args.target_extension.startswith('.') else f'.{args.target_extension}'
    
    if not os.path.exists(doc_dir):
        print(f"Error: {doc_dir} directory not found")
        return
    
    if not os.path.exists(include_dir):
        print(f"Error: {include_dir} directory not found")
        return
    
    root_path = Path(include_dir).resolve()
    images_path = Path(except_dir).resolve() if os.path.exists(except_dir) else None
    
    # Find all *_zh_Hans.adoc files
    files = find_zh_hans_files(doc_dir)
    print(f"Found {len(files)} files matching *_zh_Hans.adoc")
    print(f"Filtering links to files inside {include_dir} folder (excluding {except_dir})...")
    print(f"Including only files with extensions: {', '.join(file_extensions)}")
    print(f"Transforming targets: adding suffix '{suffix}' and changing extension to '{target_extension}'")
    if args.modify_files:
        print("⚠️  MODIFYING SOURCE FILES with transformed links")
    else:
        print("Extracting links only (use --modify-files to update source files)")
    print(f"Writing results to {output_file}...\n")
    
    all_links = []
    links_by_file = defaultdict(list)
    files_modified = 0
    
    # Process each file
    for filepath in files:
        try:
            filepath_obj = Path(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            links = extract_links(content, filepath)
            
            # Filter links to only include those pointing to files in doc/modules/ROOT folder
            # but exclude files in doc/modules/ROOT/images, and match allowed file extensions
            filtered_links = []
            for link in links:
                if link['target'] and is_link_in_root_folder(link['target'], filepath_obj, root_path, images_path, file_extensions):
                    # Transform the target: add suffix and change extension
                    original_target = link['target']
                    transformed_target = transform_link_target(original_target, suffix, target_extension)
                    
                    # Create a new link with transformed target
                    transformed_link = link.copy()
                    transformed_link['target'] = transformed_target
                    transformed_link['original_target'] = original_target
                    
                    filtered_links.append(transformed_link)
                    
                    # Replace the link in content if modifying files
                    if args.modify_files:
                        content = replace_link_in_content(
                            content,
                            link['full_match'],
                            original_target,
                            transformed_target,
                            link['type']
                        )
            
            # Write back to file if modified
            if args.modify_files and content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_modified += 1
                print(f"  Modified: {filepath} ({len(filtered_links)} links transformed)")
            
            all_links.extend(filtered_links)
            links_by_file[filepath] = filtered_links
            
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    # Calculate unique targets
    unique_targets = set()
    for link in all_links:
        if link['target']:
            unique_targets.add(link['target'])
    
    # Write output to file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write summary
        f.write("=" * 80 + "\n")
        f.write("LINK EXTRACTION SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total files processed: {len(files)}\n")
        f.write(f"Total links found (filtered to files in {include_dir} folder, excluding {except_dir}, extensions: {', '.join(file_extensions)}): {len(all_links)}\n")
        f.write(f"Targets transformed with suffix '{suffix}' and extension '{target_extension}'\n")
        f.write("\n")
        
        # Count by type
        type_counts = defaultdict(int)
        for link in all_links:
            type_counts[link['type']] += 1
        
        f.write("Links by type:\n")
        for link_type, count in sorted(type_counts.items()):
            f.write(f"  {link_type}: {count}\n")
        f.write("\n")
        
        # Write all links grouped by file
        f.write("=" * 80 + "\n")
        f.write("ALL LINKS BY FILE\n")
        f.write("=" * 80 + "\n")
        f.write("\n")
        
        for filepath, links in sorted(links_by_file.items()):
            if links:
                f.write(f"\n{filepath} ({len(links)} links):\n")
                f.write("-" * 80 + "\n")
                for i, link in enumerate(links, 1):
                    f.write(f"  {i}. [{link['type']}] {link['full_match']}\n")
                    if link.get('original_target'):
                        f.write(f"     Original Target: {link['original_target']}\n")
                    if link['target']:
                        f.write(f"     Target: {link['target']}\n")
                    if link['text']:
                        f.write(f"     Text: {link['text']}\n")
                    f.write("\n")
        
        # Write unique targets
        f.write("=" * 80 + "\n")
        f.write("UNIQUE LINK TARGETS\n")
        f.write("=" * 80 + "\n")
        
        for target in sorted(unique_targets):
            f.write(f"  {target}\n")
        
        f.write(f"\nTotal unique targets: {len(unique_targets)}\n")
    
    print(f"✓ Successfully wrote {len(all_links)} links to {output_file}")
    print(f"  - Files processed: {len(files)}")
    if args.modify_files:
        print(f"  - Files modified: {files_modified}")
    print(f"  - Unique targets: {len(unique_targets)}")

if __name__ == "__main__":
    main()

