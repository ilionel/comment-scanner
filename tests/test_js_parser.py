import unittest

from comment_scanner.parsers import common, js_parser


def extract(code):
    return [(c.text(), c.line_number(), c.is_multiline())
            for c in js_parser.extract_comments(code)]


class JsParserTest(unittest.TestCase):

    def test_comments(self):
        code = 'let a = 1; // one\n/* two\n three **/\nb() // four'
        self.assertEqual(extract(code), [(' one', 1, False),
                                         (' two\n three *', [2, 3], True),
                                         (' four', 4, False)])

    def test_unterminated_comment(self):
        with self.assertRaises(common.UnterminatedCommentError):
            extract('let a = 1; /* one')

    def test_strings(self):
        code = 'let a = "// \\" not", b = \'/* not */\'; // one'
        self.assertEqual(extract(code), [(' one', 1, False)])

    def test_template_literal(self):
        code = 'let s = `// not\n${f("// not") /* one */} /* not */`; // two'
        self.assertEqual(extract(code), [(' one ', [2], True), (' two', 2, False)])

    def test_nested_template_literal(self):
        code = 'let s = `${ {a: `// not`}.a }`; // one'
        self.assertEqual(extract(code), [(' one', 1, False)])

    def test_regex_literal(self):
        code = ('let r = /https?:\\/\\/[/*]+/g; // one\n'
                'if (x) return /\\/\\//.test(y) // two')
        self.assertEqual(extract(code), [(' one', 1, False), (' two', 2, False)])

    def test_division(self):
        code = 'let a = b / c; let d = (e) / f / g; // one'
        self.assertEqual(extract(code), [(' one', 1, False)])


if __name__ == '__main__':
    unittest.main()
