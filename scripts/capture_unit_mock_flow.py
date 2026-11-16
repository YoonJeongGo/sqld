"""Compatibility entry point for current unit-mock captures.

The archived 0.10.1 captures remain in evidence/unit-flow-capture-20261018.
Current routes, image prefixes, and output folders are owned by mock_navigation_qa.
"""
import sys
from mock_navigation_qa import main

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('test')
    main()
