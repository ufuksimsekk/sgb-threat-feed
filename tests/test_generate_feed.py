import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "generate_feed.py"
SPEC = importlib.util.spec_from_file_location("generate_feed", SCRIPT_PATH)
generate_feed = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_feed)


class FeedGenerationTests(unittest.TestCase):
    def test_normalize_ipv4_accepts_only_ipv4(self):
        self.assertEqual(generate_feed.normalize_ipv4(" 8.8.8.8 "), "8.8.8.8")
        self.assertIsNone(generate_feed.normalize_ipv4("2001:4860:4860::8888"))
        self.assertIsNone(generate_feed.normalize_ipv4("not-an-ip"))

    def test_write_feed_sorts_and_ends_with_newline(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ip.txt"
            generate_feed.write_feed({"8.8.8.8", "1.1.1.1"}, output)
            self.assertEqual(output.read_text(encoding="utf-8"), "1.1.1.1\n8.8.8.8\n")


if __name__ == "__main__":
    unittest.main()
