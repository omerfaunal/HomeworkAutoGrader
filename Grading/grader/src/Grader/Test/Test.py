import os

from Grader.Submission.Submission import Submission


class Test:
    def __init__(self, input_path, output_path):
        self.input_path: str = input_path
        self.output_path: str = output_path

    # grade the submission output against the test output
    # check if the file in the output path is the same as the file in submission output path
    def grade(self, submission: Submission):
        case_name = os.path.basename(self.input_path).replace(".in", "")
        if case_name in submission.feedback:
            return False
        submission_output_path = os.path.join(submission.submission_path,
                                              "output", os.path.basename(self.output_path))
        if not os.path.exists(submission_output_path):
            submission.feedback[case_name] = "No output file found."
            return False
        expected: str = open(self.output_path, "r").read()
        try:
            actual: str = open(submission_output_path, "r").read()
        except UnicodeDecodeError:
            submission.feedback[case_name] = "Output file decoding error."
            return False

        # check line by line, ignore empty lines and white spaces
        expected_lines = [line.strip() for line in expected.splitlines() if line.strip()]
        actual_lines = [line.strip() for line in actual.splitlines() if line.strip()]
        grade = 1
        if len(expected_lines) != len(actual_lines):
            if len(actual_lines) == 0:
                submission.feedback[case_name] = "No output file generated."
                return 0
            if expected_lines[0] == actual_lines[0]:
                grade = 0.3
                submission.feedback[case_name] = "Line2 is empty."
                return grade
            if actual_lines[0] == "Time out":
                submission.feedback[case_name] = "Timed out after 60 seconds."
                return 0
            return 0
        if expected_lines[0] != actual_lines[0]:
            grade -= 0.3
            submission.feedback[case_name] = "Line1 is wrong."
        if expected_lines[1] != actual_lines[1]:
            grade -= 0.7
            submission.feedback[case_name] = "Line2 is wrong."  
        if expected_lines[0] != actual_lines[0] and expected_lines[1] != actual_lines[1]:
            grade = 0
            submission.feedback[case_name] = "Wrong output."
        if grade == 1:
            submission.feedback[case_name] = "Passed."
        return grade
