import re
from typing import Any, Dict

_TABULAR_TAG_RE = re.compile(r"\btabular\b", re.IGNORECASE)


def kaggle_metadata_has_tabular_tag(metadata: Dict[str, Any]) -> bool:
    """True если есть тег tabular"""
    tags = metadata.get("keywords")

    if not isinstance(tags, list):
        return False
    for tag in tags:
        if _TABULAR_TAG_RE.search(str(tag)):
            return True
    return False