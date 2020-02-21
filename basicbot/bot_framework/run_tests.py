import unittest

testsuite = unittest.TestLoader().discover('test')
unittest.TextTestRunner(verbosity=2).run(testsuite)