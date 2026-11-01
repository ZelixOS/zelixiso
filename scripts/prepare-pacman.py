#!/usr/bin/env python3
"""Render a host-only local repository URL without modifying the live profile."""
import argparse
from pathlib import Path
import re


def render(text, repository):
    pattern = r'(^\[zelixrepo\][ \t]*\n)'
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    if len(matches) != 1:
        raise ValueError('Expected exactly one [zelixrepo] section')
    # Pacman does not decode percent-escaped file paths. Quoting is not supported.
    repository = Path(repository).resolve()
    if any(character.isspace() for character in str(repository)):
        raise ValueError('Build checkout path must not contain whitespace (Pacman file:// URLs).')
    return re.sub(pattern, lambda m: m.group(1) + 'Server = file://' + str(repository) + '\n',
                  text, count=1, flags=re.MULTILINE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile', type=Path)
    parser.add_argument('repository', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if not (args.repository/'zelixrepo.db').is_file():
        parser.error('Local repository index is missing; build packages first.')
    args.output.write_text(render(args.profile.read_text(), args.repository))


if __name__ == '__main__':
    main()
