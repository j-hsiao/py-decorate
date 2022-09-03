"""Extend docstrings.

Functions can often be wrapped to add some kind of functionality.  The
docstrings still apply but get covered up by any new docstring.  These
methods will prepend the old docstring to the new docstring so copy and
pasting the original docstring before the new additions is unnecessary.

extends() can be used similarly to functools.wraps, prepending a single
item's docstring.

extend() marks both methods and the class.  Decorating the class is what
causes the method docstrings to be extended.

extend_all() just finds all FunctionType/hasttr(,'__function__') members
of the class (searched with dir()) and tries to extend their docstrings.

extend() and extend_all() both use the mro() to find the base methods.
"""
from __future__ import print_function

__all__ = ['extends', 'extend', 'extend_all']

from functools import partial
from types import FunctionType
import sys
from itertools import chain

from ..utils.strutils import unindent

def extends_(thing, parents):
    """
    """
    if isinstance(thing, type):
        if sys.version_info.major > 2:
            thing.__doc__ = cls_docstr(reversed(parents + (thing,)))
    else:
        item = getattr(thing, '__func__', thing)
        docs = []
        for cand in chain(parents, (thing,)):
            if isinstance(cand, type):
                cand = getattr(cand, item.__name__, cand)
            doc = unindent(cand.__doc__)
            if not docs or docs[-1] not in doc:
                docs.append(doc)
        thing.__doc__ = '\n\n'.join(docs)
    return thing
def extends(*args):
    """Prepend the base docstring of each arg in order.

    usage:
        @extends(func1, func2, func3, ...)
        def newfunc(...):
            "new docstring here"
            ...

        result:
            approximately:
                '\n'.join(
                    map(getattr, (func1,func2,...), repeat('__doc__')))

    If a class is passed in, then search it for a member with same name
    as the decorated item.  Decorating a class will only change the
    docstring in python3 (python2 class __doc__ is readonly)
    """
    return partial(extends_, parents=args)

def attr_docstr(mro, attr):
    """Return extended docstring for attr from mro list."""
    docs = []
    last = None
    for cls in mro:
        baseitem = getattr(cls, attr, None)
        if baseitem is not None:
            doc = getattr(baseitem, '__doc__', None)
            if doc is None:
                continue
            doc = unindent(doc)
            if doc and (last is None or doc not in last):
                docs.append(doc)
                last = doc
                #name = cls.__name__
                #docs.append(
                    #''.join(('-'*(len(name)+6), '\nFrom ', name, ':')))
    return '\n\n'.join(docs[::-1]) if docs else None

def cls_docstr(mro):
    """Return the would-be extended class docstr."""
    docs = []
    for cls in mro:
        doc = cls.__doc__
        if doc:
            doc = unindent(doc)
        if doc and (not docs or doc not in docs[-1]):
            docs.append(doc)
    return '\n\n'.join(docs[::-1])

class Extend(object):
    """Temporary class to mark this item as requiring extending."""
    def __init__(self, thing):
        self.thing = thing

    def __repr__(self):
        return 'Extend({})'.format(repr(self.thing))

    def __getattr__(self, name):
        return getattr(self.thing, name)

    def __get__(self, *args, **kwargs):
        return self.thing.__get__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.thing(*args, **kwargs)


# Force user to explicitly identify attributes to extend
# docstrings.
def extend(item):
    """Mark a member for __doc__ extension or extend class.

    If item is a type:
        process any Extend attributes.
    else:
        wrap item in an Extend() instance.
    """
    if isinstance(item, type):
        mro = [cls for cls in item.mro() if cls is not object]
        for k in dir(item):
            v = getattr(item, k)
            if not isinstance(v, Extend):
                continue
            setattr(item, k, v.thing)
            v.thing.__doc__ = attr_docstr(mro, k)
        if sys.version_info.major > 2:
            item.__doc__ = cls_docstr(mro)
        return item
    else:
        if not hasattr(getattr(item, '__func__', item), '__doc__'):
            raise ValueError('extend() expects item to have a __doc__ to extend.')
        return Extend(item)

def extend_all(cls):
    """Extend all method docstrings (and class docstring if py>2).

    Use dir to detect methods.  Methods are callables which are either
    types.FunctionType or have a __function__ attribute.
    """
    mro = [c for c in cls.mro() if c is not object]
    for k in dir(cls):
        v = getattr(cls, k)
        if not isinstance(v, FunctionType):
            try:
                v = v.__func__
            except AttributeError:
                continue
        v.__doc__ = attr_docstr(mro, k)
    if sys.version_info.major > 2:
        cls.__doc__ = cls_docstr(mro)
    return cls

if __name__ == '__main__':
    class A(object):
        """A

        Class A docstr.
        """
        def __init__(self, a, b):
            """Initialize an a.

            a: arg a
            b: arg b
            """
            self.a = a
            self.b = b

        def __call__(self, a, b):
            """sum a and b."""
            return a+b

    @extend
    class B(A):
        """B

        Class B docstr.
        """
        @extend
        def __init__(self, a, b, c):
            """Initialize a b.

            c: arg c
            """
            super(B, self).__init__(a,b)
            self.c = c

        def __call__(self, a, b):
            """Double the result."""
            x = super(B, self)
            return x(a,b) + x(a,b)

        def x(self):
            """x base doc."""
            return 5

    @extend_all
    class C(B):
        """C

        Class C docstr.
        """
        mytype = set
        def __init__(self, d, **kwargs):
            """Initialize a c.

            d: arg d
            kwargs: args for b
            """
            super(C, self).__init__(**kwargs)
            self.d = d

        def __call__(self, a, b):
            ret = super(C, self)(a,b)
            print(ret)
            return ret

        def x(self):
            return super(C, self).x()
    help(C)

    def f1():
        """f1

        noop
        """
        pass

    def f2():
        """f2

        noop
        """
        pass
    def f3():
        """f3

        noop
        """
        pass

    class dummy(object):
        def f4(self):
            """dummy.f4

            also a noop
            """
            pass
    @extends(f1, f2, f3, dummy)
    def f4():
        """f4

        noop
        """
        pass
    help(f4)
