from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.utils.string.string_utils import parse_int, parse_datetime, parse_list, extract_value


class TaskDetail(BaseModel):
    """Task detail model mapped from Link Search API response fields."""
    title: str = ""
    identifier: str = ""
    doc_sub_type: str = ""
    status: str = ""
    time_spent_mn: int = 0
    time_left_mn: int = 0
    assigned_to: str = ""
    main_dev_team: list[str] = Field(default_factory=list)
    estimated_completion_date: Optional[datetime] = None
    cortex_share_link: str = ""
    importance_for_next_release: str = ""
    dependencies: list[str] = []
    estimated_start_date: Optional[datetime] = None
    estimated_end_date: Optional[datetime] = None
    parent_folder_identifier: str = ""

    @staticmethod
    def from_api_response(data: dict) -> "TaskDetail":
        """Construct a TaskDetail from a Link Search API item dict."""
        return TaskDetail(
            title=data.get("CoreField.Title", ""),
            identifier=data.get("CoreField.Identifier", ""),
            doc_sub_type=data.get("CoreField.DocSubType", ""),
            status=data.get("CoreField.Status", ""),
            time_spent_mn=parse_int(data.get("Document.TimeSpentMn", "0")),
            time_left_mn=parse_int(data.get("Document.TimeLeftMn", "0")),
            assigned_to=data.get("AssignedTo", ""),
            main_dev_team=[extract_value(item) for item in data.get("dev.Main-dev-team", []) if extract_value(item)],
            estimated_completion_date=parse_datetime(data.get("Document.CurrentEstimatedCompletionDate")),
            cortex_share_link=data.get("Document.CortexShareLinkRaw", ""),
            importance_for_next_release=extract_value(data.get("product.Importance-for-next-release", "")),
            dependencies=parse_list(data.get("Document.Dependencies", "")),
            estimated_start_date=parse_datetime(data.get("Document.CurrentEstimatedStartDate")),
            estimated_end_date=parse_datetime(data.get("Document.CurrentEstimatedEndDate")),
            parent_folder_identifier=data.get("ParentFolderIdentifier", ""),
        )
