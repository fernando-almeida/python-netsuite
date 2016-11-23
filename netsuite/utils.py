class obj(object):
    """Dictionary to object utility.

    >>> d = {'b': {'c': 2}}
    >>> x = obj(d)
    >>> x.b.c
    2
    """
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x)
                   if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b)
                   if isinstance(b, dict) else b)

