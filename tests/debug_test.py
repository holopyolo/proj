import unittest

class SimpleTest(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(1 + 1, 2)
        print("Test passed!")

if __name__ == "__main__":
    unittest.main() 