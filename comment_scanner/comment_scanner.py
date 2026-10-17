from comment_scanner.parsers import python_parser
from comment_scanner.parsers import js_parser
from comment_scanner.parsers import c_parser
from comment_scanner.parsers import swift_parser
from comment_scanner.parsers import common
import sys
from typing import List, Optional
import argparse
import os

has_magic = True
try:
    import magic
except ImportError:
    has_magic = False


MIME_MAP = {
    'text/x-c': c_parser,  # C
    'text/x-c++': c_parser,  # C++
    'text/x-c#': c_parser,  # Csharp
    'text/x-java': c_parser,  # Java
    'text/x-javascript': js_parser,  # javascript
    'text/x-python': python_parser,  # python/python3
    'text/x-go': c_parser,  # GoLang
    'text/x-swift': swift_parser,  # Swift
}

# Used when python-magic is unavailable or reports an unsupported MIME type
# (e.g. Go files are detected as text/plain).
EXTENSION_MAP = {
    '.c': 'text/x-c',
    '.h': 'text/x-c',
    '.cc': 'text/x-c++',
    '.cpp': 'text/x-c++',
    '.cxx': 'text/x-c++',
    '.hpp': 'text/x-c++',
    '.cs': 'text/x-c#',
    '.java': 'text/x-java',
    '.js': 'text/x-javascript',
    '.py': 'text/x-python',
    '.go': 'text/x-go',
    '.swift': 'text/x-swift',
}


class Error(Exception):
    """Base Error class in this module."""


class UnsupportedError(Error):
    """Raised when trying to extract comments from an unsupported MIME type."""


class ParseError(Error):
    """Raised when a parser issue is encountered."""


def fetch_from_file(filename: str, mime: Optional[str] = None) -> List[common.Comment]:
    """Extracts and returns the comments from the given file.

    Args:
      filename: String name of the file to extract comments from.
      mime: Optional MIME type for file (str). Note some MIME types accepted
        don't comply with RFC2045. If not given, an attempt to deduce the
        MIME type will occur.
    Returns:
      Python list of parsers.common.Comment in the order that they appear in the file.
    Raises:
      UnsupportedError: If filename is of an unsupported MIME type.
    """
    if not mime:
        mime = EXTENSION_MAP.get(os.path.splitext(filename)[1].lower())
        if has_magic:
            detected = _decode(magic.from_file(filename, mime=True))
            if detected in MIME_MAP or not mime:
                mime = detected
        elif not mime:
            raise ImportError('python-magic was not imported')

    with open(filename, 'r', encoding='utf-8') as code:
        return _extract(code.read(), mime)


def fetch_from_str(code: str, mime: Optional[str] = None
                   ) -> List[common.Comment]:
    """Extracts and returns comments from the given string

    Args:
      code: String      containing code to extract comments from
      mime: Optional MIME type for code (str).
    Returns:
      Python list of parsers.common.Comment in the order that they appear in the code
    Raises:
      UnsupportedError: If code is of an unsupported MIME type.
    """
    if not mime:
        if not has_magic:
            raise ImportError('python-magic was not imported')
        mime = _decode(magic.from_buffer(code.encode('utf-8'), mime=True))

    return _extract(code, mime)


def _decode(mime) -> str:
    return mime.decode('utf-8') if isinstance(mime, bytes) else mime


def _extract(code: str, mime: str) -> List[common.Comment]:
    if mime not in MIME_MAP:
        raise UnsupportedError(f"Unsupported MIME type {mime}")

    try:
        return MIME_MAP[mime].extract_comments(code)
    except common.Error as e:
        raise ParseError() from e


def main():
    """Extracts comments from files and prints them to stdout"""
    parser = argparse.ArgumentParser(
        description="Extracts comments from files and prints them to stdout"
    )
    parser.add_argument('filename', nargs='+',
                        help='File to extract comments from', type=str)
    parser.add_argument('-m', '--mime',
                        help='MIME type of file(s) to extract comments from')

    args = parser.parse_args()

    status = 0
    for filename in args.filename:
        try:
            comments = fetch_from_file(filename, args.mime)
        except (Error, ImportError, OSError) as exc:
            sys.stderr.write(f'{filename}: {exc!r}\n')
            status = 1
            continue
        for comment in comments:
            line_no = comment.line_number()
            if isinstance(line_no, list):
                line_no = line_no[0]
            print(f'{filename}:{line_no}:{comment.text()}')
    return status


if __name__ == "__main__":
    sys.exit(main())
