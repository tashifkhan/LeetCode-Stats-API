from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeVar, Generic, Union

T = TypeVar('T')

@dataclass
class ApiResponse(Generic[T]):
    """Generic API response wrapper with status and message"""
    status: str
    message: str
    data: Optional[T] = None
    
    @classmethod
    def success(cls, data: T, message: str = "retrieved"):
        return cls(
            status="success",
            message=message,
            data=data
        )
    
    @classmethod
    def error(cls, message: str, status: str = "error"):
        return cls(
            status=status,
            message=message,
            data=None
        )

# This file can be expanded with additional general response models if needed
