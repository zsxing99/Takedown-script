"""
Task executor
--------------------------------------------------
The class that handles task init, prep, and execution
"""

from takedown.task.FindRepoTask import FindRepoTask
from takedown.task.SendEmailTask import SendEmailTask


class TaskExecutor:

    def __init__(self):
        self.task = None
        self.type = None
        self.ready = False
        self.required_parameters = None
        self.optional_parameters = None
        self.execution_results = None
        self.err_msg = None

    def prepare(self, task_type: str, required_parameters: dict, optional_parameters: dict, **kwargs):
        if task_type == "find":
            self.type = "find"
            self.task = FindRepoTask()
        elif task_type == "send":
            self.type = "send"
            self.task = SendEmailTask()

        self.required_parameters = required_parameters
        self.optional_parameters = optional_parameters
        self.ready = True

        return self

    def execute(self):
        if not self.ready:
            self.err_msg = "Task executor not prepared."
            return False

        if self.type == "find":
            self.execution_results = self.task.prepare(
                self.required_parameters["GitHub_token"],
                self.required_parameters["search_query"],
                self.optional_parameters.get("inputs", None)
            ).execute(targets=self.optional_parameters.get("targets", None), chain=False)
            return self.execution_results is not None
        elif self.type == "send":
            self.execution_results = self.task.prepare(
                self.required_parameters,
                self.optional_parameters,
            ).execute()
            return self.execution_results is not None

        return False
