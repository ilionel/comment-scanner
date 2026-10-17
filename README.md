
# Comment Scanner

Comment Scanner is a Python module designed to extract comments from source code files of various types.

## Features
- **Multi-language Support**: Works with any programming language.
- **Comment Types**: Supports single-line, in-line and multi-line comments.
- **Line Numbers**: Provides the line number for each comment found.
- **CLI Tool**: Fetch comments from a file via the command line.


## Installation

Install comment scanner using pip/pip3.

```bash
pip install comment-scanner
```

MIME type detection relies on [python-magic](https://github.com/ahupp/python-magic), which needs the libmagic library (preinstalled on most Linux distributions, `brew install libmagic` on macOS). On Windows, `python-magic-bin` is installed instead and bundles it.


## API Usage
Comment can be fetched from a source code file or from string text.

```python
import comment_scanner

# to fetch comments from source file
comment_scanner.fetch_from_file('/path/of/file')

# to fetch comments from string text
comment_scanner.fetch_from_str('...')

```

Both the method returns a list of Comment object of the following structure
```
Comment(comment text, line_no, is_multiline)
```
In case of multi-line comment line_no is of List type containing all the line from the start of the comment till the end comment line.

## CLI Usage
```bash
comment_scanner <file_path> [-m or --mime <mime_type>]
```
- <file_path>: The path to the code file.
- -m or --mime <mime_type>: (Optional) The MIME type of the file.

Each comment is printed on its own line as `<file_path>:<line_no>:<comment text>` (for multi-line comments, `line_no` is the first line).


## Mime Type
Comment scanner uses python-magic module under the hood to find the mime type of a file and it works for most cases.

If python-magic is not installed, or if it reports an unsupported MIME type (Go files, for example, are detected as `text/plain`), the MIME type is deduced from the file extension.

But the user can describe the mime type of the string or file by using `mime` parameter. For supported mime-types, refer to the supported programming laguage section.


```python
import comment_scanner

comment_scanner.fetch_from_file('/path/of/main.py', mime='text/x-python')
comment_scanner.fetch_from_str('....', mime='text/x-javascript')
```

## Example
Consider `main.py` contains the following code:
```python
import requests

# The API endpoint
url = "https://jsonplaceholder.typicode.com/posts/1"

# A GET request to the API
response = requests.get(url)

# Print the response
response_json = response.json()
print(response_json)

"""
{
    'userId': 1,
    'id': 1,
    'title': 'sunt aut facere repellat provident occaecati excepturi optio reprehenderit',
    'body': 'quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto'
}
"""
```
If we want to parse all the comments present in this file, we can use comment_scanner like this

```python
import comment_scanner
comments = comment_scanner.fetch_from_file('main.py')
```
This returns the following output:
```
[Comment(The API endpoint, 3, False),
Comment(A GET request to the API, 6, False),
Comment(Print the response, 9, False),
Comment({
    'userId': 1,
    'id': 1,
    'title': 'sunt aut facere repellat provident occaecati excepturi optio reprehenderit',
    'body': 'quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto'
}, [13, 14, 15, 16, 17, 18, 19, 20], True)]
```
we can further process the comments like:
```python
...
comment_texts = []
for comment in comments:
    comment_texts.append(comment.text())

print(comment_texts)
```

## Supported Programming Language
Comment scanner currently supports the following source languages.

| Language |  mime type |
|-----|--------|
| c   | text/x-c |
| c++   | text/x-c++  |
| C#   | text/x-c# |
| java   | text/x-java |
| javascript   | text/x-javascript  |
| python   | text/x-python |
| go   | text/x-go |

And more on the way!
## Contributing

Contributions are welcome! Please [fork](https://github.com/FaizAlam/comment-scanner/fork) the repository and submit a pull request.
## License

License
This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License.
