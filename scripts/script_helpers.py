"""Common utilities for diagnostic scripts.

This module provides shared functionality to avoid duplication across
diagnostic and debugging scripts.
"""

import re
import sys
from pathlib import Path
from typing import Any


# Regex pattern for extracting quoted aliases from mapping.py
ALIAS_REGEX = r'"([^"\\]*(?:\\.[^"\\]*)"|\'([^\'\\]*(?:\\.[^\'\\]*)*)\''


def setup_import_path() -> Path:
    """Add project root to Python path and return root path."""
    root = Path(__file__).parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


def load_integration_modules() -> tuple[Any, Any, Any, Any]:
    """Load integration modules without Home Assistant runtime.
    
    Returns:
        Tuple of (scraper_mod, mapping_mod, parsing_mod, const_mod)
    """
    setup_import_path()
    
    # Import after path is set up
    from custom_components.stiebel_eltron_http import scraper, mapping, parsing, const
    
    return scraper, mapping, parsing, const


def load_test_helper():
    """Load the test module loading helper."""
    setup_import_path()
    from tests.test_scraper_localization import _load_module_from_path
    return _load_module_from_path


def extract_aliases_from_dict_str(dict_content: str) -> list[tuple[str, list[str]]]:
    """Parse HEADER_ALIASES dictionary content.
    
    Args:
        dict_content: The string content of the HEADER_ALIASES dict
        
    Returns:
        List of tuples: (canonical_key, [aliases])
    """
    # Parse the aliases - look for patterns like: KEY_NAME: [...],
    pattern = r'(\w+):\s*\[(.*?)\],'
    matches = re.findall(pattern, dict_content, re.DOTALL)
    
    result = []
    for canonical_key, aliases_str in matches:
        # Extract individual aliases (strings in quotes)
        alias_matches = re.findall(ALIAS_REGEX, aliases_str)
        
        # Extract non-empty matches (one of the two groups will match)
        aliases = [match[0] or match[1] for match in alias_matches if match[0] or match[1]]
        
        result.append((canonical_key, aliases))
    
    return result


def read_mapping_file() -> tuple[str, str]:
    """Read mapping.py file and extract HEADER_ALIASES content.
    
    Returns:
        Tuple of (full_content, header_aliases_dict_content)
    """
    mapping_file = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "mapping.py"
    content = mapping_file.read_text(encoding='utf-8')
    
    # Extract HEADER_ALIASES dictionary
    match = re.search(r'HEADER_ALIASES:\s*dict\[CanonicalKey,\s*list\[str\]\]\s*=\s*{(.*?)\n}', content, re.DOTALL)
    
    if not match:
        raise ValueError("Could not find HEADER_ALIASES in mapping.py")
    
    dict_content = match.group(1)
    return content, dict_content


def get_testdata_dir() -> Path:
    """Get the testdata directory path."""
    return Path(__file__).parent / "testdata"
