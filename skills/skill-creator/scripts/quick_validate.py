#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import argparse
import sys
import re
import yaml
from pathlib import Path

PORTABLE_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}
CLAUDE_CODE_PROPERTIES = PORTABLE_PROPERTIES | {
    'when_to_use', 'argument-hint', 'arguments', 'disable-model-invocation',
    'user-invocable', 'disallowed-tools', 'model', 'effort', 'context', 'agent',
    'background', 'hooks', 'paths', 'shell',
}
VALIDATION_TARGETS = {'portable': PORTABLE_PROPERTIES, 'claude-code': CLAUDE_CODE_PROPERTIES}


def validate_skill(skill_path, target='portable'):
    """Basic validation of a skill"""
    if target not in VALIDATION_TARGETS:
        return False, f"Unknown validation target: {target}"
    allowed_properties = VALIDATION_TARGETS[target]
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - allowed_properties
    if unexpected_keys:
        hint = ''
        if target == 'portable' and unexpected_keys <= CLAUDE_CODE_PROPERTIES:
            hint = ' For local Claude Code skills, use --target claude-code; uploads still require portable metadata.'
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties for {target} are: {', '.join(sorted(allowed_properties))}.{hint}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (kebab-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        # Check name length (max 64 characters per spec)
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        # Check for angle brackets
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"
        # Check description length (max 1024 characters per spec)
        if len(description) > 1024:
            return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    # Validate compatibility field if present (optional)
    compatibility = frontmatter.get('compatibility', '')
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > 500:
            return False, f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters."

    return True, "Skill is valid!"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate skill frontmatter for its intended host.")
    parser.add_argument("skill_directory")
    parser.add_argument("--target", choices=VALIDATION_TARGETS, default="portable")
    args = parser.parse_args()
    valid, message = validate_skill(args.skill_directory, target=args.target)
    print(message)
    sys.exit(0 if valid else 1)
