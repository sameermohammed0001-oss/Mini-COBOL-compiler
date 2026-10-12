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

            self.assertNotEqual(
                result.returncode,
                0,
                msg="Compiler should reject undeclared variable TOTAL."
            )

            self.assertIn(
                "UNDECLARED VARIABLE 'TOTAL'",
                combined_output.upper()
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

            self.assertNotEqual(
                result.returncode,
                0,
                msg="Compiler should reject 1234 in PIC 9(3)."
            )

            self.assertIn(
                "VALUE EXCEEDS PIC SIZE",
                combined_output.upper()
            )

    def test_missing_stop_run(self):
        program = VALID_PROGRAM.replace("STOP RUN.", "")

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.compile_program(program, folder)

            combined_output = result.stdout + result.stderr

            self.assertNotEqual(
                result.returncode,
                0,
                msg="Compiler should reject a program missing STOP RUN."
            )

            self.assertIn(
                "PROGRAM MUST END WITH STOP RUN",
                combined_output.upper()
            )

    def test_subtract_operation(self):
        program = VALID_PROGRAM.replace(
            "ADD NUM1 TO NUM2 GIVING RESULT.",
            "SUBTRACT NUM1 FROM NUM2."
        ).replace(
            'DISPLAY "THE FINAL RESULT IS: " RESULT.',
            'DISPLAY "THE FINAL RESULT IS: " NUM2.'
        )

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.compile_program(program, folder)

            self.assertEqual(
                result.returncode, 0,
                msg=result.stdout + result.stderr
            )

            execution = subprocess.run(
                [sys.executable, str(folder / "output.py")],
                capture_output=True,
                text=True
            )

            self.assertEqual(
                execution.returncode, 0,
                msg=execution.stdout + execution.stderr
            )
            self.assertIn("THE FINAL RESULT IS: 25", execution.stdout)

    def test_multiply_operation(self):
        program = VALID_PROGRAM.replace(
            "MOVE 25 TO NUM1.",
            "MOVE 10 TO NUM1."
        ).replace(
            "MOVE 50 TO NUM2.",
            "MOVE 5 TO NUM2."
        ).replace(
            "ADD NUM1 TO NUM2 GIVING RESULT.",
            "MULTIPLY NUM1 BY NUM2."
        ).replace(
            'DISPLAY "THE FINAL RESULT IS: " RESULT.',
            'DISPLAY "THE FINAL RESULT IS: " NUM2.'
        )

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.compile_program(program, folder)

            self.assertEqual(
                result.returncode, 0,
                msg=result.stdout + result.stderr
            )

            execution = subprocess.run(
                [sys.executable, str(folder / "output.py")],
                capture_output=True,
                text=True
            )

            self.assertEqual(
                execution.returncode, 0,
                msg=execution.stdout + execution.stderr
            )
            self.assertIn("THE FINAL RESULT IS: 50", execution.stdout)

    def test_divide_operation(self):
        program = VALID_PROGRAM.replace(
            "MOVE 25 TO NUM1.",
            "MOVE 5 TO NUM1."
        ).replace(
            "MOVE 50 TO NUM2.",
            "MOVE 100 TO NUM2."
        ).replace(
            "ADD NUM1 TO NUM2 GIVING RESULT.",
            "DIVIDE NUM1 INTO NUM2."
        ).replace(
            'DISPLAY "THE FINAL RESULT IS: " RESULT.',
            'DISPLAY "THE FINAL RESULT IS: " NUM2.'
        )

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.compile_program(program, folder)

            self.assertEqual(
                result.returncode, 0,
                msg=result.stdout + result.stderr
            )

            execution = subprocess.run(
                [sys.executable, str(folder / "output.py")],
                capture_output=True,
                text=True
            )

            self.assertEqual(
                execution.returncode, 0,
                msg=execution.stdout + execution.stderr
            )
            self.assertIn("THE FINAL RESULT IS: 20", execution.stdout)

    def test_divide_by_zero(self):
        program = VALID_PROGRAM.replace(
            "MOVE 25 TO NUM1.",
            "MOVE 0 TO NUM1."
        ).replace(
            "DIVIDE NUM1 INTO NUM2.",
            "DIVIDE NUM1 INTO NUM2."
        ).replace(
            "ADD NUM1 TO NUM2 GIVING RESULT.",
            "DIVIDE NUM1 INTO NUM2."
        )

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            result = self.compile_program(program, folder)

            self.assertEqual(
                result.returncode, 0,
                msg=result.stdout + result.stderr
            )

            execution = subprocess.run(
                [sys.executable, str(folder / "output.py")],
                capture_output=True,
                text=True
            )

            self.assertNotEqual(
                execution.returncode, 0,
                msg="Expected division by zero to raise an error."
            )
            self.assertIn(
                "Division by zero",
                execution.stderr
            )

if __name__ == "__main__":
    unittest.main(verbosity=2)
