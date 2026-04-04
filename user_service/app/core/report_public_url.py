from typing import Optional

def build_report_public_url(
    public_base_url: str,
    bucket_name: Optional[str],
    object_key: Optional[str],
) -> Optional[str]:

    base = (public_base_url or "").strip()
    if not base or not bucket_name or not object_key:
        return None
        
    b = bucket_name.strip().strip("/")
    k = object_key.lstrip("/")
    if not b or not k:
        return None
    return f"{base.rstrip('/')}/{b}/{k}"