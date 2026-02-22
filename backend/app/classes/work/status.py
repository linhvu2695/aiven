from enum import Enum


class TaskStatus(str, Enum):
    CLOSED = "closed"
    IMPLEMENTED_ON_DEV = "implemented on dev"
    IMPLEMENTED_ON_TEST = "implemented on test"
    IMPLEMENTED_ON_PROD = "implemented on prod"
    OBSOLETE = "obsolete"
    COMPLETED = "completed"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"
    ANSWERED = "answered"
    APPROVED = "approved"
    VALIDATED_ON_TEST = "validated on test"

    IN_PROGRESS = "in progress"
    NEEDS_PEER_REVIEW = "needs peer review"
    IN_DEVELOPMENT = "in development"

    BLOCKED_BY_ORANGE_LOGIC = "blocked by orange logic"
    BLOCKED_BY_CUSTOMER = "blocked by customer"
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
    TaskStatus.COMPLETED,
    TaskStatus.DUPLICATE,
    TaskStatus.REJECTED,
    TaskStatus.ANSWERED,
    TaskStatus.APPROVED,
    TaskStatus.VALIDATED_ON_TEST,
}