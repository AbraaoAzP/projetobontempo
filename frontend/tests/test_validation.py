import unittest

from services.validation import validate_contact


class ContactValidationTests(unittest.TestCase):
    def test_accepts_phone_with_supported_separators_and_digit_count(self) -> None:
        self.assertIsNone(
            validate_contact("Nome", "+55 (11) 99999-9999", "")
        )
        self.assertIsNone(validate_contact("Nome", "12345678", ""))
        self.assertIsNone(
            validate_contact("Nome", "123456789012345", "a@example.invalid")
        )

    def test_rejects_phone_with_invalid_characters_or_digit_count(self) -> None:
        for phone in ("123-ABC", "1234567", "1234567890123456", "+-() "):
            with self.subTest(phone=phone):
                message = validate_contact("Nome", phone, "")
                self.assertIsNotNone(message)
                self.assertIn("telefone", message.lower())

    def test_still_requires_name_and_phone_and_validates_email(self) -> None:
        self.assertEqual(validate_contact("", "11999999999", ""), "Informe o nome.")
        self.assertEqual(
            validate_contact("Nome", "", ""),
            "Informe o telefone.",
        )
        self.assertIn(
            "email válido",
            validate_contact("Nome", "11999999999", "invalido") or "",
        )


if __name__ == "__main__":
    unittest.main()
