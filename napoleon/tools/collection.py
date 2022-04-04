import heapq


def get_child_class(cls, include_parent=True):
    initial = {cls} if include_parent else set()
    return initial.union(set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in get_child_class(c)]))


def empty(iterables):
    return len(iterables) == 0


def leave_one_out(iterables):
    list2 = list(iterables)
    for i in range(len(list2)):
        yield list2[i], list2[:i] + list2[i+1:]


def first(iterable):
    return next(iter(iterable), None)


def last(iterable):
    return next(iter(reversed(iterable)), None)


def find_by_key(_list, key):
    return first(filter(lambda x: x.key == key, _list))


def dl_to_ld(dl):
    return [dict(zip(dl, t)) for t in zip(*dl.values())]


def ld_to_dl(ld):
    return {k: [dic[k] for dic in ld] for k in ld[0]}


def top_k(k, iterable, key=None):
    return heapq.nlargest(k, iterable, key=key)


def last_k(k, iterable, key=None):
    return heapq.nsmallest(k, iterable, key=key)


def invert_map(d):
    assert len(d.keys()) == len(set(d.values()))
    return {v: k for k, v in d.items()}
