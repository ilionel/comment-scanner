"""This module provides methods for parsing comments from C family languages

Works with:
    - c99+
    - c++
    - Objective-C
    - Java
    - C#
    - Go
"""
import re
from bisect import bisect_left
from typing import List
from comment_scanner.parsers import common


def extract_comments(code: str) -> List[common.Comment]:
    """Extracts a list of comments from the given C family source code.

    Comments are represented with the Comment class found in the common module.
    C family comments come in two forms, single and multi-line comments.
        - Single-line comments begin with '//' and continue to the end of line.
        - Multi-line comments begin with '/*' and end with '*/' and can span
        multiple lines of code. If a multi-line comment does not terminate
        before EOF is reached, then an exception is raised.

    Comment markers inside literals are ignored: strings and characters with
    escape sequences, C++ raw strings (R"(...)"), Java text blocks (triple-quoted),
    C# verbatim strings (@"...") and Go raw strings (`...`).

    Note that this doesn't take language-specific preprocessor directives into
    consideration.

    Args:
        code: String containing code to extract comments from.
    Returns:
        Python list of common. Comment in the order that they appear in the code.
    Raises:
        common.UnterminatedCommentError: Encountered an unterminated multi-line comment.
    """

    pattern = r"""
        (?P<literal>
            (?<!\w)(?:u8|[uUL])?R"(?P<delimiter>[^()\\\s"]{0,16})
                \([\s\S]*?\)(?P=delimiter)" |
            \"\"\"[\s\S]*?(?<!\\)\"\"\" |
            @"(?:[^"]|"")*" |
            "(?:\\.|[^"\\\n])*" |
            '(?:\\(?:x[0-9a-fA-F]+|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|[0-7]{1,3}|.)
                |[^'\\\n])' |
            `[^`]*`
        ) |
        (?P<single> //(?P<single_content>.*)?$) |
        (?P<multi> /\*(?P<multi_content>[\s\S]*?)\*/) |
        (?P<error> /\*)
    """

    compiled = re.compile(pattern, re.VERBOSE | re.MULTILINE)

    lines_indexes = []
    for match in re.finditer(r"$", code, re.M):
        lines_indexes.append(match.start())

    comments = []
    for match in compiled.finditer(code):
        kind = match.lastgroup
        start_character = match.start()
        line_no = bisect_left(lines_indexes, start_character)

        if kind == "single":
            comment_content = match.group("single_content")
            comment = common.Comment(comment_content, line_no + 1, multiline=False)
            comments.append(comment)

        elif kind == "multi":
            end_character = match.end()
            line_no_end = bisect_left(lines_indexes, end_character)
            line_no = [x for x in range(line_no, line_no_end + 1)]
            line_no = [x + 1 for x in line_no]
            comment_content = match.group("multi_content")
            comment = common.Comment(comment_content, line_no, multiline=True)
            comments.append(comment)

        elif kind == "error":
            raise common.UnterminatedCommentError()

    return comments
