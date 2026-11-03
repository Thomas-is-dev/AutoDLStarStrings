import json
import re
import unittest
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / 'src' / 'locales'
PLACEHOLDER = re.compile(r'\{(\w+)\}')


def load(code: str) -> dict:
    return json.loads((LOCALES_DIR / f'{code}.json').read_text(encoding='utf-8'))


class LocalesTest(unittest.TestCase):
    def test_every_locale_matches_english(self):
        english = load('en')
        for path in sorted(LOCALES_DIR.glob('*.json')):
            with self.subTest(locale=path.stem):
                catalog = load(path.stem)
                self.assertEqual(set(english), set(catalog), 'keys differ from en.json')
                for key, message in catalog.items():
                    self.assertEqual(
                        set(PLACEHOLDER.findall(english[key])),
                        set(PLACEHOLDER.findall(message)),
                        f'placeholders differ for "{key}"',
                    )


if __name__ == '__main__':
    unittest.main()
