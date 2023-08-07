import sys

from behave.__main__ import main as behave_main

# This is purely for debugging on local. Please don't add any logic here
if __name__ == "__main__":
    sys.exit(behave_main())
