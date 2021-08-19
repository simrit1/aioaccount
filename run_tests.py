import unittest
import sys

from aioaccount.tests import *   # noqa: F403, F401

if __name__ == "__main__":
    # We don't want unit test touching cli args.
    unittest.main(argv=[sys.argv[0]])
