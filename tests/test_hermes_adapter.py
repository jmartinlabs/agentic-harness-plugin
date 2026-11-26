"""Static checks for the minimal Hermes global adapter (stdlib only)."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTER_DIR = ROOT / "adapters" / "hermes"
ADAPTER_README = ADAPTER_DIR / "README.md"
MODEL_MAP_EXAMPLE = ADAPTER_DIR / "model_map.example.yaml"
PLUGIN_README = ROOT / "README.md"


class HermesAdapterTests(unittest.TestCase):
    def test_adapter_files_exist_and_do_not_duplicate_plugin_assets(self):
        self.assertTrue(ADAPTER_README.is_file(), "adapters/hermes/README.md missing")
        self.assertTrue(MODEL_MAP_EXAMPLE.is_file(), "adapters/hermes/model_map.example.yaml missing")

        # Keep the adapter minimal: no duplicated skills, roles, or methodology
        for forbidden in ("skills", "roles", "methodology"):
            self.assertFalse((ADAPTER_DIR / forbidden).exists(), f"unexpected duplicated dir: {forbidden}")
        self.assertEqual(list(ADAPTER_DIR.rglob("SKILL.md")), [], "adapter must not duplicate SKILL.md files")

    def test_plugin_readme_references_hermes_adapter(self):
        text = PLUGIN_README.read_text(encoding="utf-8")
        self.assertIn("### Hermes Agent", text)
        self.assertIn("adapters/hermes/README.md", text)
        self.assertIn("HERMES_HOME", text)

    def test_adapter_readme_covers_global_install_update_and_canonical_references(self):
        text = ADAPTER_README.read_text(encoding="utf-8")
        for expected in (
            "../../methodology/approvals.md",
            "../../methodology/dynamic-agents.md",
            "../../roles/README.md",
            "../../skills/orchestrate/SKILL.md",
            "model_map.example.yaml",
            "HERMES_HOME",
            "verify-project.py",
            "--coordinator hermes",
            "check-delegation-route",
            "### Update",
            "### Roll back",
        ):
            self.assertIn(expected, text, f"missing expected reference in Hermes adapter README: {expected}")

    def test_model_map_example_uses_list_options_and_placeholders(self):
        text = MODEL_MAP_EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("backend: model_map", text)
        self.assertIn("options:", text)
        self.assertIn("default: worker", text)

        names = re.findall(r"^\s*-\s+name:\s+(\S+)\s*$", text, flags=re.MULTILINE)
        self.assertEqual(
            names,
            ["worker", "implementation", "functional", "review", "qa", "infrastructure"],
        )

        providers = re.findall(r"^\s*provider:\s+(\S+)\s*$", text, flags=re.MULTILINE)
        models = re.findall(r"^\s*model:\s+(\S+)\s*$", text, flags=re.MULTILINE)
        self.assertEqual(len(providers), len(names))
        self.assertEqual(len(models), len(names))
        self.assertTrue(all(p == "<connected-provider>" for p in providers))
        self.assertTrue(all(m == "<verified-model>" for m in models))


if __name__ == "__main__":
    unittest.main()
