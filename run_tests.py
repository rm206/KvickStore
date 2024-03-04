import subprocess
import sys

# Build the command
command = [sys.executable, "-m", "unittest", "tests/tests.py"]

# Execute the command
subprocess.run(command)
