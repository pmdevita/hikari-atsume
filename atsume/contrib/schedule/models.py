from enum import Enum

from piccolo import columns
from piccolo.table import Table


class ScheduledTask(Table):
    class Status(str, Enum):
        SCHEDULED = "SCHEDULED"
        COMPLETE = "COMPLETE"

    id = columns.Serial(primary_key=True)
    task_name = columns.Varchar(null=True)
    task_path = columns.Varchar()
    scheduled_date = columns.Timestamptz()
    args = columns.JSON(default=list)
    kwargs = columns.JSON(default=dict)
    status = columns.Varchar(length=10, choices=Status)
