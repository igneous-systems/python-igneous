import typing
import json


def empty(x: typing.Any) -> bool:
    """Returns true if x is None, or if x doesn't have a length, or if x's length is 0
    """
    if x is None:
        return True
    # noinspection PyBroadException
    try:
        return len(x) == 0
    except:  # noinspection PyBroadException
        return False


def pretty_format(obj) -> str:
    """a JSON dumps function that never fails: if `obj` is not serializable, the returned string indicates the error
    """
    try:
        return json.dumps(obj, sort_keys=True, indent=4)
    except TypeError as e:
        return pretty_format(dict(error=str(e), data=str(obj)))

