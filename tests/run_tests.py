import unittest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == '__main__':
    # Initialize the test suite
    loader = unittest.TestLoader()
    
    # Load all test modules
    suite1 = loader.loadTestsFromName('tests.test_utils')
    suite2 = loader.loadTestsFromName('tests.debug_test')
    suite3 = loader.loadTestsFromName('tests.test_decorators')
    suite4 = loader.loadTestsFromName('tests.test_app_basic')
    suite5 = loader.loadTestsFromName('tests.test_ai_basic')
    suite6 = loader.loadTestsFromName('tests.test_local_error_analyzer')
    suite7 = loader.loadTestsFromName('tests.test_db_basics')
    
    # Combine test suites
    full_suite = unittest.TestSuite([
        suite1, suite2, suite3, suite4, suite5, suite6, suite7
    ])
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(full_suite)
    
    # Exit with non-zero code if tests failed
    if not result.wasSuccessful():
        sys.exit(1) 