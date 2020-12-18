from typing import Any, Mapping, Sequence


def merge(ds1: Any, ds2: Any, replace: bool = False) -> Any:
    if isinstance(ds1, Mapping) and isinstance(ds2, Mapping):
        append = {k: merge(ds1.get(k), v, replace) for k, v in ds2.items()}
        return {**ds1, **append}
    if isinstance(ds1, Sequence) and isinstance(ds2, Sequence):
        if replace:
            return ds2
        else:
            return tuple((*ds1, *ds2))
    else:
        return ds2


def merge_all(ds1: Any, *dss: Any, replace: bool = False) -> Any:
    res = ds1
    for ds2 in dss:
        res = merge(res, ds2, replace=replace)
    return res
