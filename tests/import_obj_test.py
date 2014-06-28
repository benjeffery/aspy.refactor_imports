import ast
import collections
import pytest

from aspy.refactor_imports.import_obj import FromImport
from aspy.refactor_imports.import_obj import FromImportSortKey
from aspy.refactor_imports.import_obj import ImportImport
from aspy.refactor_imports.import_obj import ImportImportSortKey
from aspy.refactor_imports.import_obj import namedtuple_lower


# pylint: disable=redefined-outer-name,protected-access


def test_namedtuple_lower():
    cls = collections.namedtuple('Foo', ['bar', 'baz'])
    input_instance = cls('Bar', 'Baz')
    ret = namedtuple_lower(input_instance)
    assert ret == cls('bar', 'baz')


def to_ast(s):
    return ast.parse(s).body[0]


@pytest.mark.parametrize(
    ('input_str', 'expected'),
    (
        ('from foo import bar', FromImportSortKey('foo', 'bar', '')),
        ('from foo import bar as baz', FromImportSortKey('foo', 'bar', 'baz')),
    ),
)
def test_from_import_sort_key_from_python_ast(input_str, expected):
    ast_obj = to_ast(input_str)
    assert FromImportSortKey.from_python_ast(ast_obj) == expected


@pytest.mark.parametrize(
    ('input_str', 'expected'),
    (
        ('import foo', ImportImportSortKey('foo', '')),
        ('import foo as bar', ImportImportSortKey('foo', 'bar')),
    ),
)
def test_import_import_sort_key_from_python_ast(input_str, expected):
    ast_obj = to_ast(input_str)
    assert ImportImportSortKey.from_python_ast(ast_obj) == expected


@pytest.yield_fixture
def import_import():
    yield ImportImport.from_str('import Foo as bar')


def test_import_import_ast_obj(import_import):
    assert type(import_import.ast_obj) == ast.Import


def test_import_import_import_statement(import_import):
    assert import_import.import_statement == ImportImportSortKey('Foo', 'bar')


def test_import_import_sort_key(import_import):
    assert import_import._sort_key == ImportImportSortKey('foo', 'bar')


def test_import_import_cmp():
    not_sorted = [
        ImportImport.from_str('import herp.derp'),
        ImportImport.from_str('import harp.darp'),
        ImportImport.from_str('import Foo as baz'),
        ImportImport.from_str('import Foo as bar'),
    ]
    assert sorted(not_sorted) == [
        ImportImport.from_str('import Foo as bar'),
        ImportImport.from_str('import Foo as baz'),
        ImportImport.from_str('import harp.darp'),
        ImportImport.from_str('import herp.derp'),
    ]


@pytest.mark.parametrize(
    ('input_str', 'expected'),
    (
        ('import foo', False),
        ('import foo, bar', True),
    ),
)
def test_import_import_has_multiple_imports(input_str, expected):
    assert ImportImport.from_str(input_str).has_multiple_imports is expected


@pytest.mark.parametrize(
    ('input_str', 'expected'),
    (
        ('import foo', [ImportImport.from_str('import foo')]),
        (
            'import foo, bar',
            [
                ImportImport.from_str('import foo'),
                ImportImport.from_str('import bar'),
            ],
        ),
    )
)
def test_import_import_split_imports(input_str, expected):
    assert ImportImport.from_str(input_str).split_imports() == expected


@pytest.mark.parametrize(
    'import_str',
    (
        'import foo\n',
        'import foo.bar\n',
        'import foo as bar\n',
    )
)
def test_import_import_to_text(import_str):
    assert ImportImport.from_str(import_str).to_text() == import_str


@pytest.mark.parametrize(
    ('import_str', 'expected'),
    (
        ('import   foo', 'import foo\n'),
        ('import foo   as bar', 'import foo as bar\n'),
        ('import foo as    bar', 'import foo as bar\n'),
    ),
)
def test_import_import_to_text_normalizes_whitespace(import_str, expected):
    assert ImportImport.from_str(import_str).to_text() == expected


@pytest.yield_fixture
def from_import():
    yield FromImport.from_str('from Foo import bar as baz')


def test_from_import_ast_obj(from_import):
    assert isinstance(from_import.ast_obj, ast.ImportFrom)


def test_from_import_import_statement(from_import):
    ret = from_import.import_statement
    assert ret == FromImportSortKey('Foo', 'bar', 'baz')


def test_from_import_sort_key(from_import):
    ret = from_import._sort_key
    assert ret == FromImportSortKey('foo', 'bar', 'baz')


def test_from_import_cmp():
    not_sorted = [
        FromImport.from_str('from foo import bar as baz'),
        FromImport.from_str('from foo import bar'),
        FromImport.from_str('from herp import derp'),
        FromImport.from_str('from foo import bar as buz'),
        FromImport.from_str('from foo.bar import womp'),
    ]
    assert sorted(not_sorted) == [
        FromImport.from_str('from foo import bar'),
        FromImport.from_str('from foo import bar as baz'),
        FromImport.from_str('from foo import bar as buz'),
        FromImport.from_str('from foo.bar import womp'),
        FromImport.from_str('from herp import derp'),
    ]


@pytest.mark.parametrize(
    ('input_str', 'expected'),
    (
        ('from foo import bar', False),
        ('from foo import bar, baz', True),
    ),
)
def test_from_import_has_multiple_imports(input_str, expected):
    assert FromImport.from_str(input_str).has_multiple_imports is expected


@pytest.mark.parametrize(
    ('input_str', 'expected'),
    (
        ('from foo import bar', [FromImport.from_str('from foo import bar')]),
        (
            'from foo import bar, baz',
            [
                FromImport.from_str('from foo import bar'),
                FromImport.from_str('from foo import baz'),
            ],
        ),
    ),
)
def test_from_import_split_imports(input_str, expected):
    assert FromImport.from_str(input_str).split_imports() == expected


@pytest.mark.parametrize(
    'import_str',
    (
        'from foo import bar\n',
        'from foo.bar import baz\n',
        'from foo.bar import baz as buz\n',
    ),
)
def test_from_import_to_text(import_str):
    assert FromImport.from_str(import_str).to_text() == import_str


@pytest.mark.parametrize(
    ('import_str', 'expected'),
    (
        ('from   foo import bar', 'from foo import bar\n'),
        ('from foo    import bar', 'from foo import bar\n'),
        ('from foo import   bar', 'from foo import bar\n'),
        ('from foo import bar    as baz', 'from foo import bar as baz\n'),
        ('from foo import bar as    baz', 'from foo import bar as baz\n'),
    ),
)
def test_from_import_to_text_normalizes_whitespace(import_str, expected):
    assert FromImport.from_str(import_str).to_text() == expected