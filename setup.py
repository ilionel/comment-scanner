from setuptools import setup


def readme():
    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name='comment_scanner',
    version='0.3',
    install_requires=[
        'python-magic>=0.4.27; platform_system != "Windows"',
        'python-magic-bin>=0.4.14; platform_system == "Windows"',
    ],
    description='Parse comments from various source code files',
    author='Faiz Alam',
    author_email='mohdfaizalam53@gmail.com',
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=['comment_scanner', 'comment_scanner.parsers'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent"
    ],
    url='https://github.com/FaizAlam/comment-scanner',
    python_requires='>=3.7',
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "comment_scanner = comment_scanner.comment_scanner:main",
        ],
    },

)
