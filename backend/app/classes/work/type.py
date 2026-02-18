from enum import Enum


class TaskType(str, Enum):
    ENHANCEMENT_SOFTWARE = "enhancement - software"
    ENHANCEMENT_ENGINEERING = "enhancement - engineering"
    ENHANCEMENT_MVP = "enhancement - mvp"
    DEVELOPMENT = "development"
    TDD = "tdd"

    QA = "qa"

    DEFECT_APPLICATION = "defect - application"
    DEFECT_CONFIGURATION = "defect - configuration"
    DEFECT_QA = "defect - qa"
    DEFECT_LOGS = "defect - logs"
    DEFECT_UX = "defect - ux"
    DEFECT_INFRASTRUCTURE = "defect - infrastructure"
    
    QUESTION = "question"
    CODE_REVIEW = "code review"
    MEETING = "meeting"

    TECHNICAL_VETTING = "technical vetting"
    PRODUCT_DISCOVERY = "product discovery"
    TASK_MANAGEMENT = "task management"
    DEV_PLANNING = "dev planning"
    FINAL_DEV_REVIEW = "final dev review"
    PRODUCT_REVIEW = "product review"
    UX_REVIEW = "ux review"
    FINAL_REVIEW = "final review"

    OTHER = "other"