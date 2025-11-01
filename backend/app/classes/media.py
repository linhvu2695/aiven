from enum import Enum


class MediaProcessingStatus(str, Enum):
    """Status of media processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"