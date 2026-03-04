"""Services package."""
from .mock_data import get_all_investigations, get_investigation_by_id

__all__ = [
    "get_all_investigations",
    "get_investigation_by_id",
]
