import os
from typing import List
import time

from Grader.Submission.Submission import Submission
from Grader.Test.Test import Test


class Grader:
    def __init__(self, settings):
        self.submission_dir: str = settings["submission_dir"]
        self.entry_point: str = settings["entry_point"]
        self.input_dir: str = settings["input_dir"]
        self.output_dir: str = settings["output_dir"]
        self.timeout: int = settings["timeout"]
        self.submissions: List[Submission] = []
        self.tests: List[Test] = []

    def initialize(self) -> 'Grader':
        self.init_submissions()
        self.init_tests()
        return self

    def init_submissions(self):
        for student in os.listdir(self.submission_dir):
            submission_path = os.path.join(self.submission_dir, student)
            if os.path.isdir(submission_path):
                self.submissions.append(Submission(submission_path, self.entry_point))

    def init_tests(self):
        for test in os.listdir(self.input_dir):
            if test.startswith("."):
                continue
            input_path = os.path.join(self.input_dir, test)
            output_path = os.path.join(self.output_dir, test.replace(".in", ".out"))
            if os.path.isfile(input_path) and os.path.isfile(output_path):
                self.tests.append(Test(input_path, output_path))
        pass

    def run(self):
        c = 0
        startTime = time.time()
        for submission in self.submissions:
            curretTime = time.time()
            print()
            print(f"{c+1} out of {len(self.submissions)} is processing.")
            print(f"Total elapsed time: {((curretTime - startTime)/60):.2f} minutes")
            if c!= 0:
                averageTime = (curretTime - startTime) / c
            else:
                averageTime = 0
            expectedFinishTime = averageTime * (len(self.submissions) - c)
            print(f"Expected completion time: {(expectedFinishTime/60):.2f} minutes.")
            print()
            if not submission.compiled():
                submission.ready()
                submission.compile()
            if submission.student_id == "INVALID":
                continue
            print("{id} \033[3mprocessing...\033[0m".format(id=submission.student_id))
            if not submission.valid:
                self.grade(submission)
                continue
            if not self.generated(submission):
                self.generate(submission)

            self.grade(submission)
            studentFinishTime = time.time()
            print(f"{submission.student_id} spent {(studentFinishTime - curretTime):.2f} seconds.")
            c += 1
            # print if there are check_for_illegal_imports() return true, if not don't print anything
            # if submission.check_for_illegal_imports():
            #     print("Illegal imports found in {id}".format(id=submission.student_id))
        endTime = time.time()
        print(f"Total elapsed time: {((endTime-startTime)/60):.2f}")
    def generate(self, submission):
        generated_path = os.path.join(submission.submission_path, "output")
        if not os.path.exists(generated_path):
            os.mkdir(generated_path)
        for test in self.tests:
            if not os.path.exists(os.path.join(generated_path, os.path.basename(test.input_path))):
                input_name = test.input_path.split("/")[-1]
                print(f"Running {input_name} for {submission.student_id}. ")
                submission.run(test.input_path, self.timeout)

    def generated(self, submission):
        generated_path = os.path.join(submission.submission_path, "output")
        if not os.path.exists(generated_path):
            return False
        for test in self.tests:
            output_path = os.path.join(generated_path,
                                       os.path.basename(test.input_path).replace(".in", ".out"))
            if not os.path.exists(output_path):
                return False
        return True

    def grade(self, submission):
        points_per_test = 90 / len(self.tests)
        if not submission.valid:
            print("{id} \033[3mnot valid\033[0m".format(id=submission.student_id))
            return
        if not submission.compiled():
            print("{id} \033[3mnot compiled\033[0m".format(id=submission.student_id))
            return
        submission.points += 10
        for test in self.tests:
            submission.points += points_per_test * test.grade(submission)
        print("{id} \033[3m Grade: {points}\033[0m".format(id=submission.student_id, points=submission.points))