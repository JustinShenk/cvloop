"""This modules creates the example notebook for the cvloop.functions
notebook."""

import inspect
import json
import re
import sys

sys.path.insert(0, '../cvloop')
import cvloop.functions


GENERATE_ARGS = False


def is_mod_function(mod, fun):
    """Checks if a function in a module was declared in that module.

    http://stackoverflow.com/a/1107150/3004221

    Args:
        mod: the module
        fun: the function
    """
    return inspect.isfunction(fun) and inspect.getmodule(fun) == mod


def list_functions(mod_name):
    """Lists all function declared in a module.

    http://stackoverflow.com/a/1107150/3004221

    Args:
        mod_name: the module name
    Returns:
        A list of functions declared in that module.
    """
    mod = sys.modules[mod_name]
    return [func.__name__ for func in mod.__dict__.values()
            if is_mod_function(mod, func)]


def get_linenumbers(functions, module):
    """Returns a dictionary which maps function names to line numbers.

    Args:
        functions: a list of function names
        module:    the module to look the functions up
    Returns:
        A dictionary with functions as keys and their line numbers as values.
    """
    lines = inspect.getsourcelines(module)[0]
    line_numbers = {}
    for function in functions:
        try:
            line_numbers[function] = lines.index('def {}(image):\n'.format(function)) + 1
        except ValueError:
            print(r'Can not find `def {}(image):\n`'.format(function))
            line_numbers[function] = 0
    return line_numbers


def format_doc(fun):
    """Formats the documentation in a nicer way and for notebook cells."""

    doc_lines = ['{}'.format(l) for l in
                 cvloop.functions.__dict__[fun].__doc__.split('\n')]

    mod_lines = []
    argblock = False
    returnblock = False
    for line in doc_lines:
        if 'Args:' in line:
            argblock = True
            if GENERATE_ARGS:
                mod_lines.append('**{}**\n\n'.format(
                    re.sub('^    ', '', line)))
        elif 'Returns:' in line:
            returnblock = True
            mod_lines.append('\n**{}**'.format(
                re.sub('^    ', '', line)))
        elif not argblock and not returnblock:
            mod_lines.append('{}\n'.format(re.sub('^    ', '', line)))
        elif argblock and not returnblock and ':' in line:
            if GENERATE_ARGS:
                mod_lines.append('- *{}:* {}\n'.format(
                    *re.sub('^ +', '', line).split(':')))
        elif returnblock:
            mod_lines.append(line)
        else:
            mod_lines.append('{}\n'.format(line))

    return mod_lines


def create_description_cell(fun, line_number):
    """Creates a markdown cell with a title and the help doc string of a
    function."""
    return {
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '## `cvloop.functions.{}` '.format(fun),
            '<small>[[Source](https://github.com/shoeffner/cvloop/blob/',
            'develop/cvloop/functions.py#L{})]</small>\n\n'
            .format(line_number),
            *format_doc(fun),
        ]
    }


def create_code_cell(fun):
    """Creates a code cell which uses a simple cvloop and embeds the function
    in question."""
    return {
        'cell_type': 'code',
        'metadata': {},
        'outputs': [],
        'execution_count': None,
        'source': [
            'from cvloop.functions import {}\n'.format(fun),
            'cvloop(function={}, side_by_side=True)'.format(fun)
        ]
    }


def main():
    """Main function creates the cvloop.functions example notebook."""
    notebook = {
        'cells': [
            {
                'cell_type': 'markdown',
                'metadata': {},
                'source': [
                    '# cvloop functions\n\n',
                    'This notebook shows an overview over all cvloop ',
                    'functions provided in the [`cvloop.functions` module](',
                    'https://github.com/shoeffner/cvloop/blob/',
                    'develop/cvloop/functions.py).'
                ]
            },
            {
                'cell_type': 'code',
                'metadata': {},
                'outputs': [],
                'execution_count': None,
                'source': [
                    'from cvloop import cvloop'
                ]
            },
        ],
        'nbformat': 4,
        'nbformat_minor': 1,
        'metadata': {
            'language_info': {
                'codemirror_mode': {
                    'name': 'ipython',
                    'version': 3
                },
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.5.1+'
            }
        }
    }
    functions = list_functions('cvloop.functions')

    line_numbers = get_linenumbers(functions, cvloop.functions)

    for func in functions:
        line_number = line_numbers[func]
        notebook['cells'].append(create_description_cell(func, line_number))
        notebook['cells'].append(create_code_cell(func))

    with open(sys.argv[1], 'w') as nfile:
        json.dump(notebook, nfile)


if __name__ == '__main__':
    main()
