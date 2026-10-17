import unittest

from comment_scanner.parsers import c_parser, common


def extract(code):
    return [(c.text(), c.line_number(), c.is_multiline())
            for c in c_parser.extract_comments(code)]


class CParserTest(unittest.TestCase):

    def test_comments(self):
        self.assertEqual(extract('int a; // one\n/* two\n three */'),
                         [(' one', 1, False), (' two\n three ', [2, 3], True)])

    def test_unterminated_comment(self):
        with self.assertRaises(common.UnterminatedCommentError):
            extract('int a; /* one')

    def test_escaped_quote(self):
        self.assertEqual(extract(r'char *s = "a\"// not"; // one'), [(' one', 1, False)])

    def test_char_literals(self):
        code = "char a = '\"'; // one\nchar b = '\\''; /* two */"
        self.assertEqual(extract(code), [(' one', 1, False), (' two ', [2], True)])

    def test_digit_separator(self):
        self.assertEqual(extract("int n = 1'000; // it's"), [(" it's", 1, False)])

    def test_cpp_raw_string(self):
        code = 'auto r = R"x(// not )" // not)x"; // one'
        self.assertEqual(extract(code), [(' one', 1, False)])

    def test_java_text_block(self):
        code = 'String t = """\n// not\n"""; // one'
        self.assertEqual(extract(code), [(' one', 3, False)])

    def test_csharp_verbatim_string(self):
        code = 'var p = @"C:\\// not ""/* not */"""; // one'
        self.assertEqual(extract(code), [(' one', 1, False)])

    def test_go_raw_string(self):
        code = 's := `// not\n/* not */` // one'
        self.assertEqual(extract(code), [(' one', 2, False)])


if __name__ == '__main__':
    unittest.main()
