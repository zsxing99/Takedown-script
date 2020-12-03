"""
controller submodule v0.0.1

This submodule is the controller that execute the take down process.
"""

import sys
from .InputReader import InputReader
from .InputProcessor import load_previous_outputs_as_inputs
from .TaskExecutor import TaskExecutor
from .OutputParser import parse_final_results


class MainController:

    def __init__(self):
        self.status = "init"
        self.err_msg = None

    def execute(self) -> bool:
        """
        start controller
        :return: true if
        """
        # reader
        reader = InputReader()
        if not reader.prepare():
            self.err_msg = reader.execute()
            print(self.err_msg, file=sys.stderr)
            return False

        required_params, optional_params = reader.execute()

        # processor
        if "inputs" in optional_params:
            previous_records = load_previous_outputs_as_inputs(optional_params["inputs"])
            optional_params["inputs"] = previous_records

        if "inputs" in required_params:
            previous_records = load_previous_outputs_as_inputs(required_params["inputs"])
            required_params["inputs"] = previous_records

        # executor
        executor = TaskExecutor()
        executor.prepare(reader.command_type, required_params, optional_params).execute()
        final_results = executor.execution_results
        if not final_results:
            return False

        # parser
        if not parse_final_results(final_results, optional_params.get("format", "yaml"),
                                   optional_params.get("output", None)):
            print("Output parser failed.")
        else:
            print("Program finished.")

        return True
