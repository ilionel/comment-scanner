import unittest

from comment_scanner.parsers import common, swift_parser


def extract(code):
    return [(c.text(), c.line_number(), c.is_multiline())
            for c in swift_parser.extract_comments(code)]


class SwiftParserTest(unittest.TestCase):

    def test_single_line_comment(self):
        self.assertEqual(extract('let a = 1 // one\n// two'),
                         [(' one', 1, False), (' two', 2, False)])

    def test_doc_comment(self):
        self.assertEqual(extract('/// Doc\nfunc f() {}'), [('/ Doc', 1, False)])

    def test_multi_line_comment(self):
        self.assertEqual(extract('a\n/* one\ntwo */\nb'),
                         [(' one\ntwo ', [2, 3], True)])

    def test_nested_multi_line_comment(self):
        self.assertEqual(extract('/* a /* b */ c */ // d'),
                         [(' a /* b */ c ', [1], True), (' d', 1, False)])

    def test_unterminated_comment(self):
        with self.assertRaises(common.UnterminatedCommentError):
            extract('/* a /* b */')

    def test_string_literals(self):
        code = '\n'.join([
            'let a = "// not \\" /* not */"',
            'let b = #"// not "# // one',
            'let c = """',
            '  // not',
            '  """ // two',
        ])
        self.assertEqual(extract(code), [(' one', 2, False), (' two', 5, False)])

    def test_interpolation(self):
        code = 'let s = "\\(f("// not")) // not" // one'
        self.assertEqual(extract(code), [(' one', 1, False)])

    def test_raw_string_interpolation(self):
        code = 'let s = #"\\(x) \\#(f(")"#)) // not"# // one'
        self.assertEqual(extract(code), [(' one', 1, False)])

    def test_extended_regex_literal(self):
        code = 'let r = #/https?://\\w+/# // one\n#if DEBUG // two\n#endif'
        self.assertEqual(extract(code), [(' one', 1, False), (' two', 2, False)])

    def test_crlf(self):
        self.assertEqual(extract('// one\r\nlet a = 1'), [(' one', 1, False)])


if __name__ == '__main__':
    unittest.main()
