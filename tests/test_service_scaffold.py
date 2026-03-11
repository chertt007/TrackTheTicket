from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SERVICES_DIR = ROOT / "services"


class ServiceScaffoldTests(unittest.TestCase):
    def test_all_services_have_required_foundation_files(self) -> None:
        required_paths = [
            Path("src/main.py"),
            Path("tests"),
            Path("README.md"),
            Path("Dockerfile"),
        ]
        missing: list[str] = []

        for service_dir in sorted(SERVICES_DIR.iterdir()):
            if not service_dir.is_dir():
                continue
            for rel_path in required_paths:
                candidate = service_dir / rel_path
                if not candidate.exists():
                    missing.append(str(candidate))

        self.assertEqual(missing, [], msg=f"Missing required files: {missing}")


if __name__ == "__main__":
    unittest.main()

