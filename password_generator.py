import random
import string

class PasswordGenerator:
    def __init__(self):
        self.letters = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()-_=+"

    def generate(self, length=12, n_digits=None, n_symbols=None, use_uppercase=True, base_word=""):
        """Generate a random password with base_word in the middle (unchanged order)."""

        if n_digits is None:
            n_digits = 0

        if n_symbols is None:
            n_symbols = 0

        if len(base_word) > length:
            raise ValueError("Base word is longer than total password length.")

        if length < len(base_word) + n_digits + n_symbols:
            raise ValueError("Password length too short for given base_word, digits and symbols.")

        # Remaining length for random stuff
        remaining = length - len(base_word)

        # Minimum: left + right = remaining
        left_len = random.randint(0, remaining)
        right_len = remaining - left_len

        # Generate left part
        left_chars = []
        left_chars += random.choices(self.digits, k=min(n_digits, left_len))
        left_chars += random.choices(self.symbols, k=min(n_symbols, left_len - len(left_chars)))
        left_chars += random.choices(self.letters + (self.uppercase if use_uppercase else ""),
                                     k=left_len - len(left_chars))
        random.shuffle(left_chars)

        # Generate right part
        right_chars = []
        right_digits = n_digits - sum(c in self.digits for c in left_chars)
        right_symbols = n_symbols - sum(c in self.symbols for c in left_chars)

        right_chars += random.choices(self.digits, k=right_digits)
        right_chars += random.choices(self.symbols, k=right_symbols)
        right_chars += random.choices(self.letters + (self.uppercase if use_uppercase else ""),
                                      k=right_len - len(right_chars))
        random.shuffle(right_chars)

        return ''.join(left_chars) + base_word + ''.join(right_chars)