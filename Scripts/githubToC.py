import re

# ===== CONFIGURABLE VARIABLES =====
MAX_HEADER_LEVEL = 6  # maximum header level to include (1-6). Adjust as needed.
# If you only want to include up to, say, H3, set MAX_HEADER_LEVEL = 3

# ===== INPUT: Provide your Markdown content here =====
import sys
print("Enter your Markdown text. When finished, signal EOF (Enter, then Ctrl-D):")
markdown_text = sys.stdin.read()

print("HTML Output:")
# ===== HELPER FUNCTIONS =====

def build_toc(headings):
    """
    Build a nested HTML TOC from the list of headings.
    Uses the minimum header level as the base for nesting.
    Keeps a Flat html structure bc it just seems to work better for some reason
    """
    if not headings:
        return ""
        
    # Determine the base level (minimum heading level in the content)
    base_level = min(level for level, _, _ in headings)
    
    toc_lines = []
    current_level = 0  # relative level: heading level - base_level
    toc_lines.append("<ol type='1'>")
    
    for level, text, anchor_id in headings:
        rel_level = level - base_level  # adjusted level
        # If we need to go deeper, open new <ol> tags
        while current_level < rel_level:
            toc_lines.append("<ol>") #("  " * (current_level + 1) + "<ol>")
            current_level += 1
        # If we need to step back, close open lists
        while current_level > rel_level:
            toc_lines.append("</ol>") #("  " * current_level + "</ol>")
            current_level -= 1
        # Add the list item with the <a> wrapping the <li>
        toc_lines.append(f"<a href=\"#{anchor_id}\"><li>{text}</li></a>") #("  " * (current_level + 1) + f"<a href=\"#{anchor_id}\"><li>{text}</li></a>")
    
    # Close any remaining open <ol>s
    while current_level > 0:
        toc_lines.append("</ol>") #("  " * current_level + "</ol>")
        current_level -= 1
    toc_lines.append("</ol>")
    
    return "\n".join(toc_lines)

def clean_heading(text):
    """
    Remove Markdown formatting including bold, italics, links, inline code, and images.
    """
    # Remove bold and italic markers (both ** and __, * and _)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\_\_(.*?)\_\_', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'\_(.*?)\_', r'\1', text)
    # Remove inline code markers (`code`)
    text = re.sub(r'\`([^`]*)\`', r'\1', text)
    # Replace markdown links [text](url) with just "text"
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove images ![alt](url)
    text = re.sub(r'\!\[([^\]]*)\]\([^)]+\)', r'\1', text)
    return text.strip()

def generate_anchor_id(text, used_ids):
    """
    Generate a GitHub anchor ID: lowercase, remove punctuation, and replace each space with a hyphen.
    Append a numeric suffix if the same ID is already used.
    """
    # Convert to lowercase.
    anchor = text.lower()
    # Remove punctuation: allow alphanumeric, spaces, and hyphens.
    anchor = re.sub(r'[^a-z0-9\s-]', '', anchor)
    # Replace each space with a hyphen (do not collapse multiple spaces)
    anchor = anchor.replace(" ", "-")
    anchor = anchor.strip('-')
    if anchor == "":
        anchor = "section"
    # Ensure uniqueness (if duplicate, append -1, -2, etc.)
    if anchor in used_ids:
        used_ids[anchor] += 1
        anchor_id = f"{anchor}-{used_ids[anchor]}"
    else:
        used_ids[anchor] = 0
        anchor_id = anchor
    return anchor_id

def parse_markdown_headings(markdown_text, max_header_level):
    """
    Parse the markdown text for headings up to max_header_level.
    Returns a list of tuples: (header_level, cleaned_text, anchor_id).
    """
    lines = markdown_text.splitlines()
    headings = []
    used_ids = {}
    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.*)', line)
        if not match:
            continue
        level = len(match.group(1))
        if level > max_header_level:
            continue
        heading_text = match.group(2).rstrip().rstrip('#').rstrip()
        if heading_text == "":
            continue
        clean_text = clean_heading(heading_text)
        anchor_id = generate_anchor_id(clean_text, used_ids)
        headings.append((level, clean_text, anchor_id))
    return headings

# ===== MAIN PROCESSING =====
headings = parse_markdown_headings(markdown_text, MAX_HEADER_LEVEL)
toc_html = build_toc(headings)
print(toc_html)
