#!/usr/bin/env python3
"""
Script to convert *_zh_Hans.html files to ADOC format using pypandoc,
preserving <a> tags inside <pre> blocks using regular expressions.
"""

import re
import glob
import uuid
from pathlib import Path
try:
    import pypandoc  # type: ignore
except ImportError:
    pypandoc = None

def post_process_adoc(adoc_content):
    """Post-process ADOC content to fix issues from HTML conversion."""
    
    # Remove all ++ markers that pypandoc added around special characters
    # adoc_content = adoc_content.replace('++', '')
    
    # Replace [source,cpp] with [listing,subs="+macros,+quotes"]
    # adoc_content = adoc_content.replace('[source,cpp]', '[listing,subs="+macros,+quotes"]')
    
    # Replace HTML entities with actual characters
    # Order matters: replace &amp; last to avoid interfering with other entities
    adoc_content = adoc_content.replace('&lt;', '<')
    adoc_content = adoc_content.replace('&gt;', '>')
    adoc_content = adoc_content.replace('&quot;', '"')
    adoc_content = adoc_content.replace('&apos;', "'")
    adoc_content = adoc_content.replace('&amp;', '&')  # Replace last to avoid double-processing
    
    # Add spaces before and after backtick-wrapped code if they don't exist
    # Process in two passes: one for before, one for after
    def add_space_before(match):
        """Add space before backtick code if needed."""
        before_char = match.group(1) if match.group(1) else ''
        code_block = match.group(2)  # The `...` block
        
        # Add space before if there's a non-whitespace char and it's not opening punctuation
        if before_char and not before_char.isspace() and before_char not in '([{':
            return before_char + ' ' + code_block
        return match.group(0)  # No change needed
    
    def add_space_after(match):
        """Add space after backtick code if needed."""
        code_block = match.group(1)  # The `...` block
        after_char = match.group(2) if match.group(2) else ''
        
        # Add space after if there's a non-whitespace char and it's not closing punctuation
        if after_char and not after_char.isspace() and after_char not in '.,;:!?)]}':
            return code_block + ' ' + after_char
        return match.group(0)  # No change needed
    
    # First pass: add spaces before backtick code
    # Match: (optional char before)(backtick code)
    adoc_content = re.sub(r'([^\s`]?)(`[^`]+`)', add_space_before, adoc_content)
    
    # Second pass: add spaces after backtick code
    # Match: (backtick code)(optional char after)
    adoc_content = re.sub(r'(`[^`]+`)([^\s`]?)', add_space_after, adoc_content)
    
    # Remove orphaned closing tags (like </a> without opening tag)
    adoc_content = re.sub(r'</a>', '', adoc_content)
    adoc_content = re.sub(r'</em>', '', adoc_content)
    
    return adoc_content

def convert_html_links_to_adoc_in_text(text_content):
    """Convert HTML <a> and <em> tags within text content to AsciiDoc format using regex.
    
    This function preserves HTML entities like &lt; and &gt; by using regex
    instead of BeautifulSoup, which would decode them.
    """
    # First, convert <em> tags to AsciiDoc emphasis format (_text_)
    # Handle nested tags recursively - process innermost tags first
    def replace_em_tag(em_match):
        """Replace <em> tags with AsciiDoc emphasis format."""
        em_full = em_match.group(0)
        # Extract content between <em> and </em> - handle attributes like <em class="x">
        em_inner_match = re.search(r'<em[^>]*>([\s\S]*?)</em>', em_full)
        if em_inner_match:
            em_text = em_inner_match.group(1)
            
            # Recursively process nested <em> tags first (if any)
            em_text = re.sub(r'<em[^>]*>([\s\S]*?)</em>', r'_\1_', em_text, flags=re.DOTALL)
            
            # Process nested <code> tags inside <em>
            em_text = re.sub(r'<code[^>]*>([\s\S]*?)</code>', r'`\1`', em_text, flags=re.DOTALL)
            
            # Process nested <a> tags inside <em> - convert them to links
            def replace_nested_a_tag(a_match):
                a_full = a_match.group(0)
                href_match = re.search(r'href=["\']([^"\']+)["\']', a_full)
                href = href_match.group(1) if href_match else ''
                inner_a_match = re.search(r'>([\s\S]*?)</a>', a_full)
                if inner_a_match:
                    inner_a_text = inner_a_match.group(1)
                    # Remove any remaining HTML tags
                    inner_a_text = re.sub(r'<[^>]+>', '', inner_a_text)
                    if href:
                        inner_a_text_escaped = inner_a_text.replace('[', '\\[').replace(']', '\\]')
                        return f"link:{href}[{inner_a_text_escaped}]"
                    return inner_a_text
                return a_full
            em_text = re.sub(r'<a\s+[^>]*>[\s\S]*?</a>', replace_nested_a_tag, em_text, flags=re.DOTALL)
            
            # Remove any other remaining HTML tags but preserve entities
            em_text = re.sub(r'<[^>]+>', '', em_text)
            
            # Trim whitespace and return
            em_text = em_text.strip()
            return f"_{em_text}_"
        return em_full
    
    # Convert all <em> tags - non-greedy matching handles nested tags correctly
    text_content = re.sub(r'<em[^>]*>[\s\S]*?</em>', replace_em_tag, text_content, flags=re.DOTALL)
    
    # Then convert <a> tags (which may now contain _text_ emphasis from above)
    def replace_a_tag(match):
        """Replace a single <a> tag with AsciiDoc link format."""
        full_match = match.group(0)
        
        # Extract href attribute using regex
        href_match = re.search(r'href=["\']([^"\']+)["\']', full_match)
        href = href_match.group(1) if href_match else ''
        
        # Extract inner content (everything between > and </a>)
        # Use non-greedy matching to handle nested tags
        inner_match = re.search(r'>([\s\S]*?)</a>', full_match)
        if not inner_match:
            # Self-closing tag or malformed
            return full_match
        
        inner_html = inner_match.group(1)
        
        # Process nested <code> tags within the link
        def replace_code_tag(code_match):
            code_full = code_match.group(0)
            # Extract content between <code> and </code>
            code_inner_match = re.search(r'>([\s\S]*?)</code>', code_full)
            if code_inner_match:
                code_text = code_inner_match.group(1)
                # Preserve HTML entities in code (don't decode them)
                return f"`{code_text}`"
            return code_full
        
        # Replace <code> tags with backtick-wrapped content
        inner_html = re.sub(r'<code[^>]*>[\s\S]*?</code>', replace_code_tag, inner_html, flags=re.DOTALL)
        
        # Remove any remaining HTML tags from inner content (keep only text)
        # But preserve HTML entities and already converted _text_ emphasis
        inner_text = re.sub(r'<[^>]+>', '', inner_html)
        
        # Create AsciiDoc link format: link:path[text]
        if href:
            # Escape brackets in the link text for AsciiDoc
            inner_text_escaped = inner_text.replace('[', '\\[').replace(']', '\\]')
            return f"link:{href}[{inner_text_escaped}]"
        else:
            return inner_text
    
    # Find and replace all <a> tags (including those with nested tags)
    # Pattern matches: <a ...>content</a> with any attributes
    # Use DOTALL flag to match across newlines
    pattern = r'<a\s+[^>]*>[\s\S]*?</a>'
    result = re.sub(pattern, replace_a_tag, text_content, flags=re.DOTALL)
    
    return result

def convert_html_to_adoc_preserving_pre_links(html_content):
    """Convert HTML to ADOC while preserving <a> tags inside <pre> blocks using regex.
    
    Args:
        html_content: The HTML content to convert
    """
    if pypandoc is None:
        print("  ERROR: pypandoc is not installed. Install it with: pip install pypandoc")
        return None
    
    placeholders = {}

    # Step 1: Identify and extract <pre> blocks with <a> tags using regex
    #         Replace them with unique placeholders.
    def replace_pre_with_placeholder(match):
        """Replace a <pre> tag containing <a> tags with a placeholder."""
        pre_full = match.group(0)
        pre_content = match.group(1)  # Content between <pre> and </pre>
        
        # Check if this <pre> block contains <a> tags using regex
        if re.search(r'<a[^>]*>.*?</a>', pre_content, re.DOTALL):
            # Generate a unique placeholder string
            placeholder_id = f"__PRE_LINK_PLACEHOLDER_{uuid.uuid4().hex}__"
            placeholders[placeholder_id] = pre_full  # Store the original HTML
            return placeholder_id
        else:
            # No <a> tags, return as-is
            return pre_full
    
    # Find all <pre> tags (with any attributes) and replace those with <a> tags
    # Pattern: <pre[^>]*>content</pre>
    pre_pattern = r'<pre[^>]*>([\s\S]*?)</pre>'
    modified_html = re.sub(pre_pattern, replace_pre_with_placeholder, html_content, flags=re.DOTALL)

    # Step 2: Convert the modified HTML to AsciiDoc using pypandoc
    try:
        adoc_content = pypandoc.convert_text(
            modified_html,
            'asciidoc',
            format='html',
            extra_args=['--wrap=none']  # Prevent line wrapping in code blocks
        )
    except RuntimeError as e:
        print(f"  Error during pypandoc conversion: {e}")
        return None

    # Step 3: Replace the placeholders in the AsciiDoc with the
    #         original <pre> content, wrapped in AsciiDoc literal blocks.
    if not placeholders:
        # No placeholders to replace, return as-is
        return adoc_content
    
    # First, prepare all code blocks and create mappings
    uuid_to_code_block = {}
    placeholder_to_code_block = {}
    
    for placeholder_id, original_pre_html in placeholders.items():
        # Extract inner HTML from <pre> tag using regex (preserves entities)
        pre_match = re.match(r'<pre[^>]*>([\s\S]*?)</pre>', original_pre_html, re.DOTALL)
        if pre_match:
            inner_html = pre_match.group(1)
            # Convert all <a> tags in the inner content to AsciiDoc format
            inner_content = convert_html_links_to_adoc_in_text(inner_html)
            # Wrap in AsciiDoc listing block
            adoc_code_block = f"[listing,subs=\"+macros,+quotes\"]\n----\n{inner_content}\n----"
        else:
            # Fallback: convert links and use the whole HTML
            converted_html = convert_html_links_to_adoc_in_text(original_pre_html)
            adoc_code_block = f"----\n{converted_html}\n----"
        
        # Extract UUID part for flexible matching
        uuid_part = placeholder_id.split('_')[-2]  # Get the UUID hex part
        
        # Store mappings for both exact and UUID-based matching
        placeholder_to_code_block[placeholder_id] = adoc_code_block
        uuid_to_code_block[uuid_part] = adoc_code_block
    
    # Get all <pre> blocks with links from HTML for matching (using regex)
    pre_tags_with_links = []
    for pre_match in re.finditer(r'<pre[^>]*>([\s\S]*?)</pre>', html_content, re.DOTALL):
        pre_content = pre_match.group(1)
        if re.search(r'<a[^>]*>.*?</a>', pre_content, re.DOTALL):
            pre_tags_with_links.append(pre_match.group(0))  # Store full match
    
    # Pandoc escapes underscores with ++ markers, so we need to remove them first
    # Example: __PRE_LINK_PLACEHOLDER_...__ becomes ++__++PRE++_++LINK++_++PLACEHOLDER++_++...++__++
    # Remove ++ markers FIRST so we can find placeholders in their original format
    adoc_content = adoc_content.replace('++', '')
    
    # Find ALL placeholders in ADOC content (from this run or previous runs)
    # After removing ++ markers, placeholders should be in original format
    placeholder_pattern = r'__PRE_LINK_PLACEHOLDER_([a-f0-9]+)__'
    all_placeholders_found = re.findall(placeholder_pattern, adoc_content)
    
    if not all_placeholders_found:
        # No placeholders found - this is good, means they were already replaced or pypandoc removed them
        total_placeholders = len(placeholders)
        if total_placeholders > 0:
            print(f"  No placeholders found in ADOC (pypandoc may have removed them)")
        return adoc_content
    
    # Replace all placeholders by matching with HTML <pre> blocks by order
    if len(pre_tags_with_links) == 0:
        print(f"  WARNING: Found {len(all_placeholders_found)} placeholder(s) but no <pre> blocks with links in HTML")
        return adoc_content
    
    replaced_count = 0
    for i, uuid_part in enumerate(all_placeholders_found):
        # First try to use the code block from this run's dictionary
        if uuid_part in uuid_to_code_block:
            adoc_code_block = uuid_to_code_block[uuid_part]
        elif i < len(pre_tags_with_links):
            # Match by order with HTML <pre> blocks
            pre_tag_html = pre_tags_with_links[i]
            # Extract inner HTML using regex
            pre_match = re.match(r'<pre[^>]*>([\s\S]*?)</pre>', pre_tag_html, re.DOTALL)
            if pre_match:
                inner_html = pre_match.group(1)
                inner_content = convert_html_links_to_adoc_in_text(inner_html)
                adoc_code_block = f"[listing,subs=\"+macros,+quotes\"]\n----\n{inner_content}\n----"
            else:
                print(f"  WARNING: Could not extract inner HTML from pre tag at index {i}")
                continue
        else:
            print(f"  WARNING: Placeholder {uuid_part[:8]}... has no matching <pre> block (index {i} >= {len(pre_tags_with_links)})")
            continue  # Skip if no matching <pre> block
        
        # Replace this specific placeholder (++ markers already removed at line 161)
        placeholder_to_replace = f"__PRE_LINK_PLACEHOLDER_{uuid_part}__"
        if placeholder_to_replace in adoc_content:
            adoc_content = adoc_content.replace(placeholder_to_replace, adoc_code_block, 1)
            replaced_count += 1
        else:
            print(f"  WARNING: Placeholder {placeholder_to_replace} not found in ADOC content")
    
    # Verify all were replaced (++ markers already removed)
    remaining_after = re.findall(placeholder_pattern, adoc_content)
    if remaining_after:
        print(f"  ERROR: {len(remaining_after)} placeholder(s) could not be replaced!")
        for uuid_part in remaining_after[:5]:
            print(f"    Still present: __PRE_LINK_PLACEHOLDER_{uuid_part}__")
    else:
        print(f"  Successfully replaced all {replaced_count} placeholder(s)")

    return adoc_content

def convert_html_to_adoc(html_filepath, adoc_filepath):
    """Convert HTML file to ADOC format using pypandoc with preservation of <a> tags in <pre> blocks."""
    try:
        print(f"  Converting to ADOC: {adoc_filepath}")
        # Read HTML content
        with open(html_filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Convert HTML to ADOC using the new method that preserves <a> tags in <pre> blocks
        adoc_content = convert_html_to_adoc_preserving_pre_links(html_content)
        
        if adoc_content is None:
            return False
        
        # Post-process to fix literal \n and &#160; entities
        # This must happen AFTER placeholder replacement
        adoc_content = post_process_adoc(adoc_content)
        
        # Write ADOC file (always overwrite existing file if it exists)
        with open(adoc_filepath, 'w', encoding='utf-8') as f:
            f.write(adoc_content)
        
        print(f"  Successfully converted to {adoc_filepath}")
        return True
    except Exception as e:
        print(f"  ERROR converting to ADOC: {e}")
        return False

def main():
    """Main function to process all *_zh_Hans.html files."""
    # Use the directory where this script is located as the base directory
    script_dir = Path(__file__).parent
    base_dir = script_dir
    
    # Find all *_zh_Hans.html files (original files)
    pattern = str(base_dir / '**' / '*_zh_Hans.html')
    original_files = glob.glob(pattern, recursive=True)
    
    print(f"Found {len(original_files)} original files matching *_zh_Hans.html pattern")
    print()
    
    # Convert original HTML files directly to ADOC files using regex approach
    if pypandoc is None:
        print("WARNING: Required dependencies are not installed. Skipping conversion to ADOC.")
        print("  Install pypandoc with: pip install pypandoc")
        print("  Also ensure pandoc is installed: https://pandoc.org/installing.html")
    else:
        print("Converting original HTML files to ADOC format...")
        print("(Preserving <a> tags inside <pre> blocks)")
        print()
        
        converted_count = 0
        
        for original_filepath in sorted(original_files):
            original_path = Path(original_filepath)
            # Create ADOC filepath: same name as original but with .adoc extension
            adoc_filepath = original_path.with_suffix('.adoc')
            
            # Convert HTML to ADOC (will replace all placeholders during conversion)
            if convert_html_to_adoc(original_filepath, str(adoc_filepath)):
                converted_count += 1
            print()
        
        print(f"Conversion complete. Converted {converted_count} file(s) to ADOC format.")
    
    print()
    print("All processing complete!")
    print(f"Original HTML files are unchanged.")
    print(f"ADOC files created/updated with <a> tags preserved in <pre> blocks.")

if __name__ == '__main__':
    main()

