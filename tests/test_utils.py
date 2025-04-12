import unittest
import sys
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import run_code, generate_test_code, validate_test_cases, find_failed_test_index

class TestUtils(unittest.TestCase):
    def test_run_code_without_tests(self):
        """Test running code without test cases"""
        # Test successful code execution
        result = run_code('print("Hello, World!")')
        self.assertTrue(result['success'])
        self.assertEqual(result['output'].strip(), "Hello, World!")
        self.assertIsNone(result['error'])
        
        # Test code with syntax error
        result = run_code('print("Hello, World!')
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])
        self.assertIn('SyntaxError', result['error'])
        
        # Test code with runtime error
        result = run_code('print(1/0)')
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])
        self.assertIn('ZeroDivisionError', result['error'])
        
        # Test code with timeout
        result = run_code('import time\nwhile True: time.sleep(1)')
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])
        self.assertIn('время выполнения', result['error'])
    
    def test_run_code_with_tests(self):
        """Test running code with test cases"""
        # Simple function to test
        code = "def solution(n):\n    return n * 2"
        
        # Test cases
        test_cases = [
            {"input": 5, "expected": 10, "description": "Test multiplication by 2", "output": 10},
            {"input": 0, "expected": 0, "description": "Test with zero", "output": 0},
            {"input": -5, "expected": -10, "description": "Test with negative", "output": -10}
        ]
        
        # Test successful code execution
        result = run_code(code, test_cases)
        self.assertTrue(result['success'])
        
        # Test failing code
        failing_code = "def solution(n):\n    return n + 2"
        result = run_code(failing_code, test_cases)
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])
    
    def test_generate_test_code(self):
        """Test generating test code from user code and test cases"""
        # Simple function to test
        code = "def solution(n):\n    return n * 2"
        
        # Test cases
        test_cases = [
            {"input": 5, "expected": 10, "description": "Test case 1"},
            {"input": [1, 2], "expected": 6, "description": "Test case 2"}
        ]
        
        # Generate test code
        test_code = generate_test_code(code, test_cases)
        
        # Check if the generated code includes necessary components
        self.assertIn("import unittest", test_code)
        self.assertIn("class TestSolution(unittest.TestCase)", test_code)
        self.assertIn("def test_case_1(self):", test_code)
        self.assertIn("def test_case_2(self):", test_code)
        self.assertIn("if __name__ == '__main__':", test_code)
        self.assertIn("unittest.main()", test_code)
        
        # Check if the test cases are correctly included
        self.assertIn("result = solution(5)", test_code)
        self.assertIn("self.assertEqual(result, 10)", test_code)
        self.assertIn("result = solution(1, 2)", test_code)
        self.assertIn("self.assertEqual(result, 6)", test_code)
    
    def test_validate_test_cases(self):
        """Test validation of test cases"""
        # Valid test cases
        valid_test_cases = [
            {"input": 5, "output": 10, "description": "Test case 1"},
            {"input": [1, 2], "output": 6, "description": "Test case 2"}
        ]
        self.assertTrue(validate_test_cases(valid_test_cases))
        
        # Invalid test cases - missing keys
        invalid_test_cases_1 = [
            {"input": 5, "description": "Missing output"},
            {"output": 6, "description": "Missing input"}
        ]
        self.assertFalse(validate_test_cases(invalid_test_cases_1))
        
        # Invalid test cases - not a list
        invalid_test_cases_2 = {"input": 5, "output": 10, "description": "Not a list"}
        self.assertFalse(validate_test_cases(invalid_test_cases_2))
        
        # Invalid test cases - empty list
        invalid_test_cases_3 = []
        self.assertFalse(validate_test_cases(invalid_test_cases_3))
        
        # Invalid test cases - None
        self.assertFalse(validate_test_cases(None))
    
    def test_find_failed_test_index(self):
        """Test finding the index of a failed test from error message"""
        # Error message with test case index
        error_message = "FAIL: test_case_2 (test_solution.TestSolution)\nAssertionError: 7 != 6"
        self.assertEqual(find_failed_test_index(error_message), 1)  # 0-based index
        
        # Error message without test case index
        error_message = "SyntaxError: invalid syntax"
        self.assertIsNone(find_failed_test_index(error_message))
        
        # Error message with different format
        error_message = "Error in test_case_5: expected 10 but got 12"
        self.assertIsNone(find_failed_test_index(error_message))

if __name__ == '__main__':
    unittest.main() 