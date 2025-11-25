#!/usr/bin/env python3
"""
Script to analyze Boost library documentation files and generate statistics.
Only processes main documentation types: qbk, adoc, rst, md, xml, html, mml
"""

import os
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, Tuple, List

# Main documentation types that can be converted to AsciiDoc
MAIN_TYPES = {'qbk', 'adoc', 'rst', 'md', 'xml', 'html', 'mml'}

# Directories to skip when scanning
SKIP_DIRS = {'test', 'tests', 'example', 'examples', 'build', '.git', 'include', 'src'}


def count_lines(file_path: Path) -> int:
    """Count the number of lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except (OSError, IOError):
        return 0


def get_file_extension(file_path: Path) -> str:
    """Get file extension without the dot."""
    return file_path.suffix[1:].lower() if file_path.suffix else 'no_ext'


def should_skip_directory(relative_parts: tuple) -> bool:
    """Check if directory should be skipped."""
    return any(part in SKIP_DIRS for part in relative_parts) if relative_parts else False


def is_main_type_file(file_path: Path, is_doc_dir: bool) -> bool:
    """Check if file is a main type documentation file."""
    ext = get_file_extension(file_path)

    # Only process main types
    if ext not in MAIN_TYPES:
        return False

    # Include if in doc directory or is a main type
    return is_doc_dir or ext in MAIN_TYPES


def get_relative_path(file_path: Path) -> str:
    """Get relative path from boost_1_89_0/libs, or absolute path if not relative."""
    try:
        relative_path = file_path.relative_to(Path('boost_1_89_0/libs'))
        return str(relative_path).replace('\\', '/')
    except ValueError:
        return str(file_path).replace('\\', '/')


def process_file(file_path: Path, is_doc_dir: bool,
                 stats: Dict[str, Dict[str, int]],
                 file_paths: Dict[str, List[str]]) -> None:
    """Process a single file if it's a main type."""
    if not is_main_type_file(file_path, is_doc_dir):
        return

    ext = get_file_extension(file_path)
    stats[ext]['file count'] += 1
    stats[ext]['line count'] += count_lines(file_path)
    file_paths[ext].append(get_relative_path(file_path))


def scan_library_docs(
    lib_path: Path
) -> Tuple[Dict[str, Dict[str, int]], Dict[str, List[str]]]:
    """
    Scan a library directory for main type documentation files.
    Returns statistics and file paths for main types only.
    """
    stats = defaultdict(lambda: {'file count': 0, 'line count': 0})
    file_paths = defaultdict(list)

    for root, _, files in os.walk(lib_path):
        root_path = Path(root)

        # Get relative parts for skipping logic
        if root_path == lib_path:
            relative_parts = ()
        else:
            try:
                relative_parts = root_path.relative_to(lib_path).parts
            except ValueError:
                relative_parts = root_path.parts

        # Skip certain directories
        if should_skip_directory(relative_parts):
            continue

        # Check if we're in a documentation directory
        is_doc_dir = 'doc' in root_path.parts

        # Process files
        for file in files:
            file_path = root_path / file
            process_file(file_path, is_doc_dir, stats, file_paths)

    # Convert to regular dict and filter out empty entries
    result = {ext: data for ext, data in stats.items() if data['file count'] > 0}
    return result, dict(file_paths)


def sort_stats(stats: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
    """Return a dict sorted by descending file count, then extension name."""
    return {
        ext: stats[ext]
        for ext in sorted(
            stats.keys(),
            key=lambda ext: (-stats[ext]['file count'], ext)
        )
    }


def collect_libraries_by_type(lib_stats: Dict[str, Dict[str, Dict[str, int]]],
                              main_type: str) -> List[Dict[str, Dict[str, int]]]:
    """Collect all libraries that have a specific main type."""
    libraries_with_type = []
    for lib_name, lib_data in lib_stats.items():
        if main_type in lib_data:
            libraries_with_type.append({
                lib_name: {
                    "file count": lib_data[main_type].get('file count', 0),
                    "line count": lib_data[main_type].get('line count', 0)
                }
            })
    return libraries_with_type


def sort_libraries_by_file_count(
    libraries: List[Dict[str, Dict[str, int]]]
) -> List[Dict[str, Dict[str, int]]]:
    """Sort libraries by file count (descending), then by library name."""
    return sorted(
        libraries,
        key=lambda x: (
            -list(x.values())[0]['file count'],
            list(x.keys())[0]
        )
    )


def get_top_libraries(libraries: List[Dict[str, Dict[str, int]]],
                     min_count: int) -> Dict[str, Dict[str, int]]:
    """Get top libraries, merged into a single dict."""
    top_count = min_count if len(libraries) >= min_count else len(libraries)
    top_libraries = libraries[:top_count]

    merged = {}
    for lib in top_libraries:
        merged.update(lib)
    return merged


def create_type_data(main_type: str,
                    lib_stats: Dict[str, Dict[str, Dict[str, int]]],
                    total_stats: Dict[str, Dict[str, int]],
                    min_top_libraries: int) -> Dict[str, Any]:
    """Create data structure for a single main type."""
    type_data = {
        "_total": {
            "file count": total_stats.get(main_type, {}).get('file count', 0),
            "line count": total_stats.get(main_type, {}).get('line count', 0)
        },
        "top libraries": {}
    }

    libraries_with_type = collect_libraries_by_type(lib_stats, main_type)
    sorted_libraries = sort_libraries_by_file_count(libraries_with_type)
    type_data["top libraries"] = get_top_libraries(sorted_libraries, min_top_libraries)

    return type_data


def create_main_types_by_type(lib_stats: Dict[str, Dict[str, Dict[str, int]]],
                              total_stats: Dict[str, Dict[str, int]],
                              min_top_libraries: int = 5) -> Dict[str, Any]:
    """
    Create structure organized by file type with totals and top libraries.
    """
    result = {}

    for main_type in sorted(MAIN_TYPES):
        result[main_type] = create_type_data(
            main_type, lib_stats, total_stats, min_top_libraries
        )

    # Add file types list at the beginning
    result = {"file types": list(sorted(MAIN_TYPES))} | result
    return result


def create_total_main_types_stats(
    lib_stats: Dict[str, Dict[str, Dict[str, int]]]
) -> Dict[str, Any]:
    """
    Create statistics for all libraries, only for main types.
    """
    result = {}
    for lib_name, lib_data in sorted(lib_stats.items()):
        # Only include main types (already filtered, but double-check)
        main_types_only = {
            ext: stats for ext, stats in lib_data.items() if ext in MAIN_TYPES
        }
        if main_types_only:
            result[lib_name] = main_types_only
    return result


def get_library_directories(boost_libs_path: Path) -> List[Path]:
    """Get all library directories to analyze."""
    return sorted([
        d for d in boost_libs_path.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ])


def analyze_single_library(
    lib_dir: Path
) -> Tuple[Dict[str, Dict[str, int]], Dict[str, List[str]]]:
    """Analyze a single library and return its statistics."""
    lib_name = lib_dir.name
    print(f"Analyzing {lib_name}...")

    lib_stats, lib_file_paths = scan_library_docs(lib_dir)
    return lib_stats, lib_file_paths


def accumulate_totals(lib_stats: Dict[str, Dict[str, int]],
                      total_stats: Dict[str, Dict[str, int]]) -> None:
    """Accumulate library statistics into totals."""
    for ext, data in lib_stats.items():
        if ext in MAIN_TYPES:
            total_stats[ext]['file count'] += data['file count']
            total_stats[ext]['line count'] += data['line count']


def save_statistics_files(main_types_lib_stats: Dict[str, Dict[str, Dict[str, int]]],
                          total_stats: Dict[str, Dict[str, int]],
                          all_file_paths: Dict[str, List[str]]) -> None:
    """Save all statistics files."""
    # Save main types by type
    main_types_output_file = 'boost_doc_statistics_main.json'
    main_types_by_type = create_main_types_by_type(
        main_types_lib_stats,
        total_stats,
        min_top_libraries=5
    )
    with open(main_types_output_file, 'w', encoding='utf-8') as f:
        json.dump(main_types_by_type, f, indent=2, ensure_ascii=False)

    # Save total statistics
    output_file = 'boost_doc_statistics_total.json'
    total_main_types_stats = create_total_main_types_stats(main_types_lib_stats)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(total_main_types_stats, f, indent=2, ensure_ascii=False)

    # Save file list for conversion
    file_list_output = 'boost_doc_files_to_convert.json'
    sorted_file_paths = {ext: sorted(paths) for ext, paths in all_file_paths.items()}
    with open(file_list_output, 'w', encoding='utf-8') as f:
        json.dump(sorted_file_paths, f, indent=2, ensure_ascii=False)

    print("\nAnalysis complete!")
    print(
        f"  Main types by type (with totals & top libraries) "
        f"saved to: {main_types_output_file}"
    )
    print(f"  All libraries main types statistics saved to: {output_file}")
    print(f"  File list for conversion saved to: {file_list_output}")


def main():
    """Main function to analyze all Boost libraries."""
    boost_libs_path = Path('boost_1_89_0/libs')

    if not boost_libs_path.exists():
        print(f"Error: {boost_libs_path} does not exist!")
        return

    libraries = get_library_directories(boost_libs_path)
    print(f"Found {len(libraries)} libraries to analyze...")

    main_types_lib_stats = {}
    total_stats = defaultdict(lambda: {'file count': 0, 'line count': 0})
    all_file_paths = defaultdict(list)

    # Analyze each library
    for lib_dir in libraries:
        lib_stats, lib_file_paths = analyze_single_library(lib_dir)

        if lib_stats:
            lib_name = lib_dir.name
            sorted_lib_stats = sort_stats(lib_stats)
            main_types_lib_stats[lib_name] = sorted_lib_stats

            # Merge file paths
            for ext, paths in lib_file_paths.items():
                all_file_paths[ext].extend(paths)

            # Accumulate totals
            accumulate_totals(lib_stats, total_stats)

    # Save all output files
    save_statistics_files(main_types_lib_stats, total_stats, all_file_paths)
    print(f"Total libraries analyzed: {len(main_types_lib_stats)}")


if __name__ == '__main__':
    main()
