from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

from src.generators.contract_generator import TEMPLATE_DIR, generate
from src.generators.template_loader import BLANK


class ContractGeneratorTest(unittest.TestCase):
    def test_generates_searchable_good_and_bad_pair_with_answer_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            manifest = generate(
                output_dir=output, template_dir=TEMPLATE_DIR,
                keys=["murabaha"], pairs=1, seed=42,
            )
            self.assertEqual(2, len(manifest))
            good = PdfReader(output / "good" / "murabaha-001-good.pdf")
            bad = PdfReader(output / "bad" / "murabaha-001-bad.pdf")
            good_text = " ".join(page.extract_text() or "" for page in good.pages)
            bad_text = " ".join(page.extract_text() or "" for page in bad.pages)
            self.assertIn("one fixed Contract Price", good_text)
            self.assertIn("EIBOR plus 3%", bad_text)
            self.assertIsNone(BLANK.search(good_text))
            saved = json.loads((output / "manifest.json").read_text())
            self.assertEqual("variable and uncertain sale price", saved[1]["expected_seeded_issues"][1])
            self.assertTrue((output / "ANSWER-KEY.md").is_file())


if __name__ == "__main__":
    unittest.main()
