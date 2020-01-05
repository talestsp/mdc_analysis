import unittest
import datetime
import time


if __name__ == "__main__":
    init_test_time = datetime.datetime.now()

    loader = unittest.TestLoader()

    suite1 = loader.discover('tests', pattern="*_test.py")

    all_tests = unittest.TestSuite(suite1)
    unittest.TextTestRunner(verbosity=2).run(all_tests)

    end_test_time = datetime.datetime.now()

    total_time = end_test_time - init_test_time

    time.sleep(2)

    print(total_time.seconds, "seconds")
    print(total_time.seconds / 60, "minutes")