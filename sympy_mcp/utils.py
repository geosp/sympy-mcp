"""Utilities for per-tool instruction loading."""
import re
from pathlib import Path


def load_tool_instruction(filename: str, module_path: str, tool_name: str) -> str:
    """Load the header + a specific tool's section from an instructions.md file.

    Each instructions.md has a structure like:
        # Feature Title
        General preamble text...
        ---
        ## tool_name_1
        Tool-specific docs...
        ---
        ## tool_name_2
        Tool-specific docs...

    This function returns the header (everything before the first ---)
    concatenated with only the ``## tool_name`` section for the requested tool.
    If the section is not found, falls back to the entire file contents.
    """
    filepath = Path(module_path).parent / filename
    content = filepath.read_text()

    # Split on --- delimiters (typically on their own line)
    sections = re.split(r"\n---\n", content)

    # First section is the header / preamble
    header = sections[0].strip() if sections else ""

    # Search remaining sections for the one starting with ## tool_name
    tool_section = None
    for section in sections[1:]:
        stripped = section.strip()
        first_line = stripped.split("\n", 1)[0].strip()
        if first_line == f"## {tool_name}":
            tool_section = stripped
            break

    if tool_section is None:
        # Fallback: return entire file contents
        return content

    return f"{header}\n\n---\n\n{tool_section}"
