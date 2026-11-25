"""A generated project is complete and passes its own tests."""
from __future__ import annotations

import os
import subprocess
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KIT)

import new_project  # noqa: E402


def test_generated_project_passes_its_tests(tmp_path):
    target = new_project.create("Test Harbour Logistics", "port logistics", dest=str(tmp_path), test=False)
    assert os.path.basename(target) == "test-harbour-logistics"
    r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
                       cwd=target, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-3000:]


def test_placeholders_filled_and_skills_copied(tmp_path):
    target = new_project.create("Acme Clinic", "outpatient clinic", slug="acme", dest=str(tmp_path),
                                git=False, test=False)
    assert new_project.leftovers(target) == []
    assert "Acme Clinic" in open(os.path.join(target, "CLAUDE.md")).read()
    skills = set(os.listdir(os.path.join(target, ".claude", "skills")))
    assert {"company-spec", "sim-build", "ml-models", "closed-loop-test", "case-study"} <= skills
    assert "new-company-sim" not in skills
    assert os.path.exists(os.path.join(target, "docs", "PLAYBOOK.md"))


def test_every_skill_has_frontmatter():
    skills = os.path.join(KIT, ".claude", "skills")
    for name in os.listdir(skills):
        text = open(os.path.join(skills, name, "SKILL.md")).read()
        assert text.startswith("---\n"), name
        head = text.split("---")[1]
        assert f"name: {name}" in head and "description:" in head, name
