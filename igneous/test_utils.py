import pytest
import igneous


class _foo:
    def __str__(self):
        return "_foo"


def test_pretty_print():
    assert igneous.pretty_print(dict(a="1", b=2)) == '{\n    "a": "1",\n    "b": 2\n}'
    assert igneous.pretty_print(_foo()) == \
           '{\n    "data": "_foo",\n    "error": "Object of type _foo is not JSON serializable"\n}'
