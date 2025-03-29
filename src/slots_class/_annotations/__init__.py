import sys
from typing import Any, Iterable


__all__ = ["annotations_from_ns"]


def _annotations_from_ns(namespace: dict[str, Any]) -> Iterable[str]:
    return namespace.get("__annotations__", {})


if sys.version_info < (3, 14):
    annotations_from_ns = _annotations_from_ns

else:
    from annotationlib import call_annotate_function, Format

    def annotations_from_ns(namespace: dict[str, Any]) -> Iterable[str]:
        try:
            return call_annotate_function(namespace["__annotate__"], Format.FORWARDREF)

        except KeyError:
            return _annotations_from_ns(namespace)
