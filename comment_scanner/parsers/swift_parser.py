"""This module provides methods for parsing comments from Swift code."""
from bisect import bisect_left
from typing import List
from comment_scanner.parsers import common


def extract_comments(code: str) -> List[common.Comment]:
    """Extracts a list of comments from the given Swift source code.

    Comments are represented with the Comment class found in the common module.
    Swift comments come in two forms, single and multi-line comments.
        - Single-line comments begin with '//' and continue to the end of line.
          Documentation comments ('///') are single-line comments whose text
          starts with '/'.
        - Multi-line comments begin with '/*' and end with '*/'. Unlike C, they
          can be nested: '/* a /* b */ c */' is a single comment. If a
          multi-line comment does not terminate before EOF is reached, then an
          exception is raised.

    Comment markers inside string literals are ignored. This covers single-line
    ("...") and multi-line (\"\"\"...\"\"\") strings, raw strings (#"..."#),
    string interpolation and extended regex literals (#/.../#).

    Args:
        code: String containing code to extract comments from.
    Returns:
        Python list of common.Comment in the order that they appear in the code.
    Raises:
        common.UnterminatedCommentError: Encountered an unterminated multi-line comment.
    """
    scanner = _Scanner(code)
    scanner.scan_code()
    return scanner.comments


class _Scanner():
    """Walks Swift source code and collects its comments."""

    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.comments = []
        self._newlines = [i for i, char in enumerate(code) if char == '\n']

    def line_of(self, index: int) -> int:
        """Returns the 1-based line number of the character at index."""
        return bisect_left(self._newlines, index) + 1

    def scan_code(self, in_interpolation: bool = False):
        """Scans code until EOF, or until the ')' closing an interpolation."""
        code = self.code
        depth = 0
        while self.pos < len(code):
            char = code[self.pos]
            if code.startswith('//', self.pos):
                self.single_line_comment()
            elif code.startswith('/*', self.pos):
                self.multi_line_comment()
            elif char in ('"', '#'):
                self.literal()
            elif in_interpolation and char == '(':
                depth += 1
                self.pos += 1
            elif in_interpolation and char == ')':
                self.pos += 1
                if depth == 0:
                    return
                depth -= 1
            else:
                self.pos += 1

    def single_line_comment(self):
        end = self.code.find('\n', self.pos)
        if end == -1:
            end = len(self.code)
        text = self.code[self.pos + 2:end].rstrip('\r')
        line_no = self.line_of(self.pos)
        self.comments.append(common.Comment(text, line_no, multiline=False))
        self.pos = end

    def multi_line_comment(self):
        code = self.code
        start = self.pos
        index = start + 2
        depth = 1
        while index < len(code):
            if code.startswith('/*', index):
                depth += 1
                index += 2
            elif code.startswith('*/', index):
                depth -= 1
                index += 2
                if depth == 0:
                    break
            else:
                index += 1
        if depth:
            raise common.UnterminatedCommentError()

        line_no = list(range(self.line_of(start), self.line_of(index - 1) + 1))
        text = code[start + 2:index - 2]
        self.comments.append(common.Comment(text, line_no, multiline=True))
        self.pos = index

    def literal(self):
        """Skips a string or extended regex literal starting at the current position.

        Anything else starting with '#' (e.g. '#if', '#selector') is skipped
        one character at a time.
        """
        code = self.code
        hashes = 0
        while code.startswith('#', self.pos + hashes):
            hashes += 1
        start = self.pos + hashes

        if code.startswith('"', start):
            self.string(start, hashes)
        elif hashes and code.startswith('/', start):
            self.regex(start, hashes)
        else:
            self.pos += 1

    def string(self, start: int, hashes: int):
        code = self.code
        multiline = code.startswith('"""', start)
        delimiter = ('"""' if multiline else '"') + '#' * hashes
        escape = '\\' + '#' * hashes
        self.pos = start + (3 if multiline else 1)

        while self.pos < len(code):
            if code.startswith(delimiter, self.pos):
                self.pos += len(delimiter)
                return
            if code.startswith(escape, self.pos):
                self.pos += len(escape)
                if code.startswith('(', self.pos):
                    self.pos += 1
                    self.scan_code(in_interpolation=True)
                else:
                    self.pos += 1
                continue
            if code[self.pos] == '\n' and not multiline:
                # Unterminated single-line string, resume scanning on next line.
                return
            self.pos += 1

    def regex(self, start: int, hashes: int):
        code = self.code
        delimiter = '/' + '#' * hashes
        self.pos = start + 1

        while self.pos < len(code):
            if code.startswith(delimiter, self.pos):
                self.pos += len(delimiter)
                return
            self.pos += 2 if code[self.pos] == '\\' else 1
