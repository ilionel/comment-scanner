import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

import comment_scanner
from comment_scanner import comment_scanner as scanner


class CommentScannerTest(unittest.TestCase):

    def write(self, name, content):
        tmp_dir = tempfile.mkdtemp()
        path = os.path.join(tmp_dir, name)
        with open(path, 'w', encoding='utf-8') as code:
            code.write(content)
        self.addCleanup(os.remove, path)
        return path

    def test_fetch_from_str_with_mime(self):
        comments = comment_scanner.fetch_from_str('int a = 1; // one', mime='text/x-c')
        self.assertEqual([c.text() for c in comments], [' one'])

    def test_fetch_from_str_unsupported(self):
        with self.assertRaises(scanner.UnsupportedError):
            comment_scanner.fetch_from_str('x', mime='text/x-unknown')

    def test_fetch_from_file_go_extension(self):
        path = self.write('main.go', 'package main\n// one\n')
        comments = comment_scanner.fetch_from_file(path)
        self.assertEqual([c.text() for c in comments], [' one'])

    def test_fetch_from_file_extension_without_magic(self):
        path = self.write('main.go', '// one\n')
        with mock.patch.object(scanner, 'has_magic', False):
            comments = comment_scanner.fetch_from_file(path)
        self.assertEqual([c.text() for c in comments], [' one'])

    def test_fetch_from_file_swift_extension(self):
        path = self.write('main.swift', 'import Foundation\n// one\n')
        comments = comment_scanner.fetch_from_file(path)
        self.assertEqual([c.text() for c in comments], [' one'])

    def test_parse_error(self):
        with self.assertRaises(scanner.ParseError):
            comment_scanner.fetch_from_str('/* a', mime='text/x-c')

    def test_cli_prints_comments_of_every_file(self):
        first = self.write('a.go', '// one\n')
        second = self.write('b.go', 'var b = 2\n/* two\n */\n')
        out = StringIO()
        argv = ['comment_scanner', first, second]
        with mock.patch('sys.argv', argv), redirect_stdout(out):
            status = scanner.main()
        self.assertEqual(status, 0)
        self.assertEqual(out.getvalue().splitlines(),
                         [f'{first}:1: one', f'{second}:2: two', ' '])


if __name__ == '__main__':
    unittest.main()
