
__all__ = [
    # text
    'check_name',
    'parse_name_pattern',
    'parse_tag_pattern',
    'parse_selections',
    'iter_clean_lines',
    'flatten_strings',
    # classes
    'as_namedtuple',
    # filesystem
    'temporary_file',
    'check_file',
    'check_dir',
    # platform
    'MS_WINDOWS',
    'run_command',
]


#######################################
# text utils

from collections import namedtuple


def check_name(name, *, loose=False, allownumeric=False):
    if not name or not isinstance(name, str):
        raise ValueError(f'bad name {name!r}')
    if allownumeric:
        name = f'_{name}'
    if not loose:
        if name.startswith('-'):
            raise ValueError(name)
        if not name.replace('-', '_').isidentifier():
            raise ValueError(name)


def parse_name_pattern(text, *, fail=True):
    name = text
    # XXX Support globs and/or regexes?  (return a callable)
    try:
        check_name('_' + name)
    except Exception:
        if fail:
            raise  # re-raise
        return None
    return name


def parse_tag_pattern(text):
    if not text.startswith('<'):
        return None
    if not text.endswith('>'):
        return None
    tag = text[1:-1]
    # XXX Support globs and/or regexes?  (return a callable)
    check_name(tag)
    return tag


def parse_selections(selections, parse_entry=None):
    if isinstance(selections, str):
        selections = selections.split(',')
    if parse_entry is None:
        parse_entry = (lambda o, e: (o, e, None, e))

    for entry in selections:
        entry = entry.strip()
        if not entry:
            continue

        op = '+'
        if entry.startswith('-'):
            op = '-'
            entry = entry[1:]

        yield parse_entry(op, entry)


def iter_clean_lines(filename):
    with open(filename, encoding="utf-8") as reqsfile:
        for line in reqsfile:
            # strip comment
            line = line.partition('#')[0]
            line = line.rstrip()
            if not line:
                continue
            yield line


def flatten_strings(values, *, coerce=False, split=False):
    """Yield all the strings in the possibly nested given values.

    "values" may be:

     * a string
     * an iterable of strings (or of iterables of strings, etc.)
    """
    if split is True:
        def split(value):
            return value.replace(',', ' ').split()
    elif split:
        raise NotImplementedError(repr(split))
    if isinstance(values, str):
        values = split(values) if split else [values]
        return iter(values)
    seen = set()
    return _flatten_strings(values, coerce, split, seen)


def _flatten_strings(values, coerce, split, seen_iterables):
    seen_iterables.add(id(values))
    for value in values:
        if isinstance(value, str):
            if coerce:
                value = str(value)
            if split:
                yield from split(value)
            else:
                yield value
        elif id(value) not in seen_iterables:
            yield from _flatten_strings(value, coerce, seen_iterables)


#######################################
# classes

from collections import namedtuple


def as_namedtuple(cls, *fields, inherit=True):
    """Return a new namedtuple subclass that inherits from the given class.

    This may be used as a class decorator factory.
    """
    if not isinstance(cls, type):
        # It was used as a decoratyr factory.
        fields = list(flatten_strings((cls, *fields), split=True))
        def decorator(cls):
            return _as_namedtuple(cls, fields, inherit)
        return decorator
    else:
        fields = list(flatten_strings((cls, *fields), split=True))
        return _as_namedtuple(cls, fields, inherit)


def _as_namedtuple(cls, fields, inherit):
    if not fields:
        raise NotImplementedError
    if not isinstance(cls, type):
        raise TypeError(f'expected a class, got {cls!r}')
    if type(cls) is not type:
        raise NotImplementedError(cls)
    if cls.__bases__ != (object,):
        # Deal with namedtuple base classes.
        ntbases = [b for b in cls.__bases__
                   if issubclass(b, tuple) and hasattr(b, '_fields')]
        #if len(ntbases) == 1:
        #    base, = ntbases
        #    if not inherit:
        #        raise TypeError(f'{cls} has incompatible base {base}')
        #    fields = (*base._fields, *fields)
        #elif ntbases:
        #    raise TypeError(f'{cls} can have at most 1 namedtuple base class, got {ntbases}')
        if ntbases:
            raise TypeError(f'{cls} must not have any namedtuple base classes, got {ntbases}')
        # Deal with base classes that define __new__().
        if cls.__new__ is not object.__new__ and cls.__new__ not in vars(cls):
            # for now we assume no base classes handle super() corrctly
            raise NotImplementedError(cls)

    bases = (
        cls,
        # XXX Insert a NamedTupleFixes here?
        namedtuple(cls.__name__, fields),
    )
    ns = {
        '__slots__': (),
    }
    return type(cls.__name__, bases, ns)


#######################################
# filesystem utils

import contextlib
import errno
import os
import os.path
import shlex
import shutil
import subprocess
import sys
import tempfile


@contextlib.contextmanager
def temporary_file():
    tmp_filename = tempfile.mktemp()
    try:
        yield tmp_filename
    finally:
        try:
            os.unlink(tmp_filename)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise


def check_file(filename):
    if not os.path.isabs(filename):
        raise ValueError(f'expected absolute path, got {filename!r}')
    if not os.path.isfile(filename):
        raise ValueError(f'file missing ({filename})')


def check_dir(dirname):
    if not os.path.isabs(dirname):
        raise ValueError(f'expected absolute path, got {dirname!r}')
    if not os.path.isdir(dirname):
        raise ValueError(f'directory missing ({dirname})')


def resolve_file(filename, relroot=None):
    resolved = os.path.normpath(filename)
    resolved = os.path.expanduser(resolved)
    #resolved = os.path.expandvars(filename)
    if not os.path.isabs(resolved):
        if not relroot:
            relroot = os.getcwd()
        elif not os.path.isabs(relroot):
            raise NotImplementedError(relroot)
        resolved = os.path.join(relroot, resolved)
    return resolved


def safe_rmtree(path):
    if not os.path.exists(path):
        return False

    print("Remove directory %s" % path)
    # XXX Pass onerror to report on any files that could not be deleted?
    shutil.rmtree(path)
    return True


#######################################
# platform utils

import logging
import subprocess
import sys


MS_WINDOWS = (sys.platform == 'win32')


def run_cmd(argv, *, env=None, capture=None, verbose=True):
    try:
        cmdstr = ' '.join(shlex.quote(a) for a in argv)
    except TypeError:
        print(argv)
        raise  # re-raise

    if capture is True:
        capture = 'both'
    kw = dict(
        env=env,
    )
    if capture == 'both':
        kw.update(dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ))
    elif capture == 'combined':
        kw.update(dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ))
    elif capture == 'stdout':
        kw.update(dict(
            stdout=subprocess.PIPE,
        ))
    elif capture == 'stderr':
        kw.update(dict(
            stderr=subprocess.PIPE,
        ))
    elif capture:
        raise NotImplementedError(repr(capture))
    if capture:
        kw.update(dict(
            encoding='utf-8',
        ))

    # XXX Use a logger.
    if verbose:
        print('#', cmdstr)

    # Explicitly flush standard streams, required if streams are buffered
    # (not TTY) to write lines in the expected order
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        proc = subprocess.run(argv, **kw)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            if verbose:
                print('command failed (not found)')
            return 127, None, None
        raise
    if proc.returncode != 0 and verbose:
        print(f'Command failed with exit code {proc.returncode}')
    return proc.returncode, proc.stdout, proc.stderr


def run_python(*args, python=sys.executable, **kwargs):
    if not isinstance(python, str) and python is not None:
        try:
            # See _pythoninfo.get_info().
            python = python.sys.executable
        except AttributeError:
            raise TypeError(f'expected python str, got {python!r}')
    return run_cmd([python, *args], **kwargs)


#######################################
# network utils

import urllib.request


def download(url, filename):
    response = urllib.request.urlopen(url)
    with response:
        content = response.read()

    with open(filename, 'wb') as fp:
        fp.write(content)
        fp.flush()
