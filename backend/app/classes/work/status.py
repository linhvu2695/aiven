from enum import Enum


class TaskStatus(str, Enum):
    CLOSED = "closed"
    IMPLEMENTED_ON_DEV = "implemented on dev"
    IMPLEMENTED_ON_TEST = "implemented on test"
    IMPLEMENTED_ON_PROD = "implemented on prod"
    OBSOLETE = "obsolete"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"
    VALIDATED_ON_TEST = "validated on test"
    VALIDATED_ON_PROD = "validated on prod"

    IN_PROGRESS = "in progress"
    NEEDS_PEER_REVIEW = "needs peer review"
    IN_DEVELOPMENT = "in development"

    BLOCKED_BY_ORANGE_LOGIC = "blocked by orange logic"
    ON_HOLD = "on hold"
    
    TO_BE_VETTED = "to be vetted"
    TO_DISPATCH = "to dispatch"
    GATHERING_REQUIREMENTS = "gathering requirements"
    READY_TO_START = "ready to start"
    REOPENED = "reopened"

COMPLETE_STATUSES = {
    TaskStatus.CLOSED, 
    TaskStatus.IMPLEMENTED_ON_DEV,
    TaskStatus.IMPLEMENTED_ON_TEST,
    TaskStatus.IMPLEMENTED_ON_PROD,
    TaskStatus.OBSOLETE,
    TaskStatus.CANCELLED,
    TaskStatus.COMPLETED,
    TaskStatus.DUPLICATE,
    TaskStatus.REJECTED,
    TaskStatus.VALIDATED_ON_TEST,
    TaskStatus.VALIDATED_ON_PROD,
}