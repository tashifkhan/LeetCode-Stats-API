from dataclasses import asdict
from typing import Any, Dict, Optional

from models.canonical.constants import PLATFORM


def make_envelope(username: str, data: Any, legacy: Optional[Dict[str, Any]] = None, cached: bool = False, status: str = "success", message: str = "retrieved", platform: str = PLATFORM) -> Dict[str, Any]:
    envelope: Dict[str, Any] = {}
    if legacy:
        envelope.update(legacy)
    envelope.setdefault("status", status)
    envelope.setdefault("message", message)
    envelope["platform"] = platform
    envelope["username"] = username
    envelope["cached"] = cached
    envelope["data"] = asdict(data) if hasattr(data, "__dataclass_fields__") else data
    return envelope
