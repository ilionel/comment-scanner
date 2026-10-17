"""This module provides methods for parsing comments from Javascript code."""

from comment_scanner.parsers import common

# Keywords after which a '/' starts a regular expression rather than a division.
REGEX_KEYWORDS = {
    'await', 'case', 'delete', 'do', 'else', 'in', 'instanceof', 'new', 'of',
    'return', 'throw', 'typeof', 'void', 'yield',
}


def extract_comments(code):
    """Extracts a list of comments from the given Javascript source code.

    Comments are represented with the Comment class found in the common module.
    Javascript comments come in two forms, single and multi-line comments.
        - Single-line comments begin with '//' and continue to the end of line.
        - Multi-line comments begin with '/*' and end with '*/' and can span
          multiple lines of code.
    If a multi-line comment does not terminate before EOF is reached,
    then an exception is raised.

    Comment markers inside string literals ('...', "..."), template literals
    (`...`, including ${...} substitutions) and regular expression literals
    (/.../) are ignored.

    Args:
        code: String containing code to extract comments from.
    Returns:
        Python list of common.Comment in the order that they appear in the code.
    Raises:
        common.UnterminatedCommentError: Raised if an unterminated multi-line
        comment is encountered.
    """
    scanner = _Scanner(code)
    scanner.scan_code()
    return scanner.comments


class _Scanner():
    """Walks Javascript source code and collects its comments."""

    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.comments = []
        # Whether a '/' at the current position would start a regex literal.
        self.regex_allowed = True

    def advance(self, count=1):
        self.line += self.code.count('\n', self.pos, self.pos + count)
        self.pos += count

    def scan_code(self, in_substitution=False):
        """Scans code until EOF, or until the '}' closing a ${...} substitution."""
        code = self.code
        depth = 0
        while self.pos < len(code):
            char = code[self.pos]
            if code.startswith('//', self.pos):
                self.single_line_comment()
            elif code.startswith('/*', self.pos):
                self.multi_line_comment()
            elif char in ('"', "'"):
                self.string(char)
                self.regex_allowed = False
            elif char == '`':
                self.template()
                self.regex_allowed = False
            elif char == '/' and self.regex_allowed:
                self.regex()
                self.regex_allowed = False
            elif char.isalnum() or char in ('_', '$'):
                start = self.pos
                while self.pos < len(code) and (code[self.pos].isalnum()
                                                or code[self.pos] in ('_', '$')):
                    self.pos += 1
                self.regex_allowed = code[start:self.pos] in REGEX_KEYWORDS
            elif char.isspace():
                self.advance()
            else:
                self.advance()
                if in_substitution and char == '{':
                    depth += 1
                elif in_substitution and char == '}':
                    if depth == 0:
                        return
                    depth -= 1
                self.regex_allowed = char not in (')', ']')

    def single_line_comment(self):
        end = self.code.find('\n', self.pos)
        if end == -1:
            end = len(self.code)
        text = self.code[self.pos + 2:end]
        self.comments.append(common.Comment(text, self.line))
        self.pos = end

    def multi_line_comment(self):
        end = self.code.find('*/', self.pos + 2)
        if end == -1:
            raise common.UnterminatedCommentError()
        start_line = self.line
        text = self.code[self.pos + 2:end]
        self.advance(end - self.pos)
        line_no = [x for x in range(start_line, self.line + 1)]
        self.comments.append(common.Comment(text, line_no, multiline=True))
        self.advance(2)

    def string(self, quote):
        code = self.code
        self.advance()
        while self.pos < len(code):
            char = code[self.pos]
            if char == quote:
                self.advance()
                return
            if char == '\n':
                # Unterminated string, resume scanning on next line.
                return
            self.advance(2 if char == '\\' else 1)

    def template(self):
        code = self.code
        self.advance()
        while self.pos < len(code):
            if code[self.pos] == '`':
                self.advance()
                return
            if code.startswith('${', self.pos):
                self.advance(2)
                self.regex_allowed = True
                self.scan_code(in_substitution=True)
                continue
            self.advance(2 if code[self.pos] == '\\' else 1)

    def regex(self):
        code = self.code
        index = self.pos + 1
        in_class = False
        while index < len(code) and code[index] != '\n':
            char = code[index]
            if char == '\\':
                index += 1
            elif char == '[':
                in_class = True
            elif char == ']':
                in_class = False
            elif char == '/' and not in_class:
                self.pos = index + 1
                return
            index += 1
        # Not a valid regex literal, treat '/' as an operator.
        self.advance()
