import unittest
import re
from password_generator import PasswordGenerator

class TestPasswordGenerator(unittest.TestCase):
    # Setup the test environment
    def setUp(self):
        self.generator = PasswordGenerator()

    def test_generate_basic_password(self):
        """Test generating a basic password with default settings"""
        password = self.generator.generate(12, 2, 2)
        self.assertEqual(len(password), 12)
        self.assertTrue(any(c.isdigit() for c in password))  # Check for digits
        self.assertTrue(any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password))  # Check for symbols
        self.assertTrue(any(c.isupper() for c in password))  # Check for uppercase

    def test_generate_password_with_word(self):
        """Test generating a password with a specific word"""
        word = "test"
        password = self.generator.generate(12, 2, 2, True, word)
        self.assertEqual(len(password), 12)
        self.assertTrue(word in password.lower())  # Check if word is included
        self.assertTrue(any(c.isdigit() for c in password))  # Check for digits
        self.assertTrue(any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password))  # Check for symbols

    def test_generate_password_no_uppercase(self):
        """Test generating a password without uppercase letters"""
        password = self.generator.generate(12, 2, 2, False)
        self.assertEqual(len(password), 12)
        self.assertTrue(any(c.isdigit() for c in password))  # Check for digits
        self.assertTrue(any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password))  # Check for symbols
        self.assertFalse(any(c.isupper() for c in password))  # Check no uppercase

    def test_generate_password_length(self):
        """Test generating passwords of different lengths"""
        lengths = [8, 12, 16, 20]
        for length in lengths:
            password = self.generator.generate(length, 2, 2)
            self.assertEqual(len(password), length)

    def test_generate_password_digits(self):
        """Test generating passwords with different numbers of digits"""
        digits = [0, 2, 4, 6]
        for num_digits in digits:
            password = self.generator.generate(12, num_digits, 2)
            digit_count = sum(1 for c in password if c.isdigit())
            self.assertEqual(digit_count, num_digits)

    def test_generate_password_symbols(self):
        """Test generating passwords with different numbers of symbols"""
        symbols = [0, 2, 4, 6]
        for num_symbols in symbols:
            password = self.generator.generate(12, 2, num_symbols)
            symbol_count = sum(1 for c in password if c in "!@#$%^&*()_+-=[]{}|;:,.<>?")
            self.assertEqual(symbol_count, num_symbols)

    def test_generate_password_zero_length(self):
        """Test generating password with zero length"""
        with self.assertRaises(ValueError):
            self.generator.generate(0, 2, 2)

    def test_generate_password_negative_digits(self):
        """Test generating password with negative number of digits"""
        with self.assertRaises(ValueError):
            self.generator.generate(12, -1, 2)

    def test_generate_password_negative_symbols(self):
        """Test generating password with negative number of symbols"""
        with self.assertRaises(ValueError):
            self.generator.generate(12, 2, -1)

    def test_generate_password_total_length_exceeded(self):
        """Test generating password where digits + symbols exceed total length"""
        with self.assertRaises(ValueError):
            self.generator.generate(12, 7, 7)

    def test_generate_password_word_too_long(self):
        """Test generating password with word longer than total length"""
        with self.assertRaises(ValueError):
            self.generator.generate(12, 2, 2, True, "thiswordistoolong")

    def test_generate_password_unique(self):
        """Test that generated passwords are unique"""
        passwords = set()
        for _ in range(100):
            password = self.generator.generate(12, 2, 2)
            self.assertNotIn(password, passwords)
            passwords.add(password)

if __name__ == '__main__':
    unittest.main() 