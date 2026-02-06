#!/usr/bin/env python3
"""
Collect all Boost library names and their GitHub paths from boostorg/boost.

1. Fetches .gitmodules from https://github.com/boostorg/boost (master).
2. For each submodule in libs/, fetches meta/libraries.json from the repo
   at the given release version (e.g. boost-1.90.0) or develop if not given.
3. Extracts library name and GitHub path from each libraries.json entry.
4. Writes the list in the format: name_or_key, repo_url.git, "ref", "subpath"
   (no sorting; order follows .gitmodules and libraries.json order)

Usage:
    python collect_boost_libraries.py [--version BOOST_VERSION] [--output FILE]
    python collect_boost_libraries.py --version boost-1.90.0 -o list.txt
"""

import argparse
import json
import os
import re
import sys
from typing import List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GITMODULES_URL = "https://raw.githubusercontent.com/boostorg/boost/master/.gitmodules"
# {repo} = submodule name, {ref} = branch/tag (e.g. develop, boost-1.90.0)
LIBS_JSON_TEMPLATE = (
    "https://raw.githubusercontent.com/boostorg/{repo}/{ref}/meta/libraries.json"
)
REPO_URL_TEMPLATE = "https://github.com/boostorg/{repo}.git"
DEFAULT_REF = "develop"
USER_AGENT = "BoostLibraryList/1.0"


def quoted(s: str) -> str:
    """Return string wrapped in double quotes with internal quotes escaped."""
    return '"' + s.replace('"', '""') + '"'


def fetch_url(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_gitmodules(content: str) -> List[Tuple[str, str]]:
    """Parse .gitmodules and return list of (submodule_name, path)."""
    PATH_PREFIX = "path = "
    URL_PREFIX = "url = "
    
    entries = []
    current_name = None
    current_path = None
    for line in content.splitlines():
        line = line.strip()
        m = re.match(r'\[submodule\s+"([^"]+)"\]', line)
        if m:
            if current_name is not None and current_path is not None:
                entries.append((current_name, current_path))
            current_name = m.group(1)
            current_path = None
            continue
        if line.startswith(PATH_PREFIX):
            current_path = line[len(PATH_PREFIX):].strip()
        elif line.startswith(URL_PREFIX):
            pass  # we use submodule name for repo, path for libs/tools
    if current_name is not None and current_path is not None:
        entries.append((current_name, current_path))
    return entries


def get_libraries_from_repo(submodule_name: str, ref: str) -> List[Tuple[str, str, str]]:
    """
    Fetch meta/libraries.json for a submodule at ref (branch/tag).
    Returns list of (first_column, repo_url, subpath).
    - Root library (key == submodule): first_column = key, subpath = "".
    - Sub-library: first_column = name, subpath = path relative to repo (e.g. "minmax").
    """
    url = LIBS_JSON_TEMPLATE.format(repo=submodule_name, ref=ref)
    try:
        content = fetch_url(url)
    except HTTPError as e:
        if e.code == 404:
            return []
        raise
    except URLError:
        return []

    try:
        raw = json.loads(content)
    except json.JSONDecodeError:
        return []

    # Support both array ([{...}, ...]) and single object ({...}) formats
    if isinstance(raw, list):
        libs = raw
    elif isinstance(raw, dict):
        libs = [raw]
    else:
        return []

    repo_url = REPO_URL_TEMPLATE.format(repo=submodule_name)
    result = []
    for obj in libs:
        if not isinstance(obj, dict):
            continue
        name = obj.get("name") or obj.get("key", "")
        key = obj.get("key", "")
        if not name or not key:
            continue
        # Root: key == submodule -> first_col = key, subpath = ""
        # Sub: key is submodule/path -> first_col = name, subpath = relative path
        if key == submodule_name:
            first_column = key
            subpath = ""
        else:
            prefix = submodule_name + "/"
            first_column = name
            subpath = key[len(prefix) :] if key.startswith(prefix) else key
        result.append((first_column, repo_url, subpath))
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Collect Boost library names and GitHub paths"
    )
    parser.add_argument(
        "--version",
        "-v",
        metavar="REF",
        default=None,
        help="Release version or branch (e.g. boost-1.90.0). Default: develop",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="boost_libraries_list.txt",
        help="Output file path (default: boost_libraries_list.txt)",
    )
    args = parser.parse_args()

    # Validate output path
    out_path = args.output
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        print(f"Error: Output directory '{out_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    ref = args.version if args.version is not None else DEFAULT_REF
    print(f"Using ref for libraries.json: {ref}", file=sys.stderr)
    print("Fetching .gitmodules from boostorg/boost...", file=sys.stderr)
    
    # Fetch .gitmodules with error handling
    try:
        gitmodules = fetch_url(GITMODULES_URL)
    except HTTPError as e:
        print(f"Failed to fetch .gitmodules: HTTP {e.code} - {e.reason}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Failed to fetch .gitmodules: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error fetching .gitmodules: {e}", file=sys.stderr)
        sys.exit(1)
    
    submodules = parse_gitmodules(gitmodules)
    # Only submodules under libs/
    lib_submodules = [(n, p) for n, p in submodules if p.startswith("libs/")]
    print(f"Found {len(lib_submodules)} libs submodules.", file=sys.stderr)

    all_libraries = []
    seen = set()  # (first_col, repo_url, subpath) to avoid duplicates

    for i, (submodule_name, path_in_boost) in enumerate(lib_submodules, 1):
        print(f"  [{i}/{len(lib_submodules)}] {submodule_name} ...", 
              file=sys.stderr, end=" ", flush=True)
        try:
            libs = get_libraries_from_repo(submodule_name, ref)
            for first_col, repo_url, subpath in libs:
                key = (first_col, repo_url, subpath)
                if key not in seen:
                    seen.add(key)
                    all_libraries.append((first_col, repo_url, subpath))
            print(len(libs), file=sys.stderr)
        except (HTTPError, URLError, json.JSONDecodeError) as e:
            print(f"error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"unexpected error: {e}", file=sys.stderr)

    # Check if any libraries were found
    if not all_libraries:
        print("Warning: No libraries found!", file=sys.stderr)
        sys.exit(1)

    # Write output file with error handling
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            for first_col, repo_url, subpath in all_libraries:
                subpath_quoted = quoted(subpath) if subpath else '""'
                line = (
                    f"{quoted(first_col)}, {quoted(repo_url)}, "
                    f"{quoted(ref)}, {subpath_quoted}\n"
                )
                f.write(line)
    except IOError as e:
        print(f"Failed to write output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Wrote {len(all_libraries)} libraries to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
