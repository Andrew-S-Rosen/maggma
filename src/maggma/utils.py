# coding: utf-8
"""
Utilities to help with maggma functions
"""
import itertools
import signal
import logging

from datetime import datetime, timedelta

from pydash.utilities import to_path
from pydash.objects import set_, get, has
from pydash.objects import unset as _unset

# import tqdm Jupyter widget if running inside Jupyter
try:
    # noinspection PyUnresolvedReferences
    if get_ipython().__class__.__name__ == "ZMQInteractiveShell":  # type: ignore
        from tqdm import tqdm_notebook as tqdm
    else:  # likely 'TerminalInteractiveShell'
        from tqdm import tqdm
except NameError:
    from tqdm import tqdm


def primed(iterable):
    """Preprimes an iterator so the first value is calculated immediately
       but not returned until the first iteration
    """
    itr = iter(iterable)
    try:
        first = next(itr)  # itr.next() in Python 2
    except StopIteration:
        return itr
    return itertools.chain([first], itr)


class TqdmLoggingHandler(logging.Handler):
    """
    Helper to enable routing tqdm progress around logging
    """

    def __init__(self, level=logging.NOTSET):
        """
        Initialize the Tqdm handler
        """
        super().__init__(level)

    def emit(self, record):
        """
        Emit a record via Tqdm screen
        """
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


def confirm_field_index(store, fields):
    """Confirm index on store for at least one of fields

    One can't simply ensure an index exists via
    `store.collection.create_index` because a Builder must assume
    read-only access to source Stores. The MongoDB `read` built-in role
    does not include the `createIndex` action.

    Returns:
        True if an index exists for a given field
        False if not

    """
    if not isinstance(fields, list):
        fields = [fields]
    info = store.collection.index_information().values()
    for spec in (index["key"] for index in info):
        for field in fields:
            if spec[0][0] == field:
                return True
    return False


def dt_to_isoformat_ceil_ms(dt):
    """Helper to account for Mongo storing datetimes with only ms precision."""
    return (dt + timedelta(milliseconds=1)).isoformat(timespec="milliseconds")


def isostr_to_dt(s):
    """Convert an ISO 8601 string to a datetime."""
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")


# This lu_key prioritizes not duplicating potentially expensive item
# processing on incremental rebuilds at the expense of potentially missing a
# source document updated within 1 ms of a builder get_items call. Ensure
# appropriate builder validation.
LU_KEY_ISOFORMAT = (isostr_to_dt, dt_to_isoformat_ceil_ms)


def recursive_update(d, u):
    """
    Recursive updates d with values from u

    Args:
        d (dict): dict to update
        u (dict): updates to propogate
    """

    for k, v in u.items():
        if k in d:
            if isinstance(v, dict) and isinstance(d[k], dict):
                recursive_update(d[k], v)
            else:
                d[k] = v
        else:
            d[k] = v


def grouper(iterable, n):
    """
    Collect data into fixed-length chunks or blocks.
    >>> list(grouper(3, 'ABCDEFG'))
    [['A', 'B', 'C'], ['D', 'E', 'F'], ['G']]

    Updated from:
    https://stackoverflow.com/questions/31164731/python-chunking-csv-file-multiproccessing/31170795#31170795
    """
    iterable = iter(iterable)
    return iter(lambda: list(itertools.islice(iterable, n)), [])


def lazy_substitute(d, aliases):
    """
    Simple top level substitute that doesn't dive into mongo like strings
    """
    for alias, key in aliases.items():
        if key in d:
            d[alias] = d[key]
            del d[key]


def substitute(d, aliases):
    """
    Substitutes keys in dictionary
    Accepts multilevel mongo like keys
    """
    for alias, key in aliases.items():
        if has(d, key):
            set_(d, alias, get(d, key))
            unset(d, key)


def unset(d, key):
    """
    Unsets a key
    """
    _unset(d, key)
    path = to_path(key)
    for i in reversed(range(1, len(path))):
        if len(get(d, path[:i])) == 0:
            unset(d, path[:i])


class Timeout:
    """
    Context manager that provides context.
    implementation courtesy of https://stackoverflow.com/a/22348885/637562
    """

    def __init__(self, seconds=14, error_message=""):
        """
        Set a maximum running time for functions.

        :param seconds (int): Seconds before TimeoutError raised, set to None to disable,
        default is set assuming a maximum running time of 1 day for 100,000 items
        parallelized across 16 cores, i.e. int(16 * 24 * 60 * 60 / 1e5)
        :param error_message (str): Error message to display with TimeoutError
        """
        self.seconds = int(seconds) if seconds else None
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        """
        Raises an error on timeout
        """
        raise TimeoutError(self.error_message)

    def __enter__(self):
        """
        Enter context with timeout
        """
        if self.seconds:
            signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        """
        Exit context with timeout
        """
        if self.seconds:
            signal.alarm(0)