import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
COMPILER = PROJECT_DIR / "src" / "compiler.py"

VALID_PROGRAM = """
IDENTIFICATION DIVISION.
PROGRAM-ID. TESTPROG.
DATA DIVISION.
WORKING-STORAGE SECTION.
01 NUM1 PIC 9(3).
01 NUM2 PIC 9(3).
01 RESULT PIC 9(4).
PROCEDURE DIVISION.
    MOVE 25 TO NUM1.
    MOVE 50 TO NUM2.
    ADD NUM1 TO NUM2 GIVING RESULT.
    DISPLAY "THE FINAL RESULT IS: " RESULT.
    STOP RUN.
"""

INVALID_PROGRAM = VALID_PROGRAM.replace(
    "GIVING RESULT.",
    "GIVING TOTAL."
)


class TestMiniCobolCompiler(unittest.TestCase):

    def compile_program(self, source, folder):
        source_file = folder / "test_input.cbl"
        source_file.write_text(source, encoding="utf-8")

        return subprocess.run(
            [sys.executable, str(COMPILER), str(source_file)],
            cwd=folder,
            capture_output=True,
            text=True
        )

    def test_valid_program(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.compile_program(VALID_PROGRAM, folder)

            self.assertEqual(
                result.returncode,
                0,
                msg=result.stdout + result.stderr
            )

            output_file = folder / "output.py"
            self.assertTrue(output_file.exists())

            execution = subprocess.run(
                [sys.executable, str(output_file)],
                capture_output=True,
                text=True
            )

            self.assertEqual(
                execution.returncode,
                0,
                msg=execution.stdout + execution.stderr
            )

            self.assertIn(
                "THE FINAL RESULT IS: 75",
                execution.stdout
            )

    def test_undeclared_variable(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.compile_program(INVALID_PROGRAM, folder)

            combined_output = result.stdout + result.stderr

            self.assertTrue(
                result.returncode != 0
                or "TOTAL" in combined_output.upper(),
                msg="Expected an error for undeclared variable TOTAL."
            )

    def test_numeric_value_exceeds_pic_size(self):
        program = VALID_PROGRAM.replace(
            "MOVE 25 TO NUM1.",
            "MOVE 1234 TO NUM1."
        )

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.compile_program(program, folder)

            combined_output = result.stdout + result.stderr

            self.assertTrue(
                result.returncode != 0
                or "exceed" in combined_output.lower()
                or "too large" in combined_output.lower()
                or "overflow" in combined_output.lower(),
                msg="Expected an error for value 1234 in PIC 9(3)."
            )

    def test_missing_stop_run(self):
        program = VALID_PROGRAM.replace("STOP RUN.", "")

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.compile_program(program, folder)

            combined_output = result.stdout + result.stderr

            self.assertTrue(
                result.returncode != 0
                or "stop run" in combined_output.lower(),
                msg="Expected an error when STOP RUN is missing."
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
