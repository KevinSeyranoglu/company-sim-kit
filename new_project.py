"""Create a new company simulation repository from starter/.

    python new_project.py "Maple Ridge Bakery" --industry "industrial bakery" --dest ~/Desktop/Projects

Copies starter/ to <dest>/<slug>, fills the {{PLACEHOLDERS}}, copies the phase skills to
.claude/skills/, PLAYBOOK.md to docs/, briefs/<slug>.md to docs/BRIEF.md if it exists, runs git init
and the starter's tests. Nothing is committed or pushed.
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
STARTER = os.path.join(KIT, "starter")
SKILLS = os.path.join(KIT, ".claude", "skills")
KIT_ONLY_SKILLS = {"new-company-sim"}          # starts projects; not needed inside one
TEXT = {".py", ".md", ".txt", ".yml", ".yaml", ".sql", ".json", ".toml", ".cfg", ".gitignore"}
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "data", "figures", "results")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fill(root, values):
    for folder, _, files in os.walk(root):
        if ".git" in folder.split(os.sep):
            continue
        for f in files:
            path = os.path.join(folder, f)
            if os.path.splitext(f)[1] not in TEXT and f not in TEXT:
                continue
            text = open(path, encoding="utf-8").read()
            new = text
            for key, value in values.items():
                new = new.replace("{{" + key + "}}", value)
            if new != text:
                open(path, "w", encoding="utf-8").write(new)


def leftovers(root):
    hits = []
    for folder, _, files in os.walk(root):
        if ".git" in folder.split(os.sep):
            continue
        for f in files:
            path = os.path.join(folder, f)
            try:
                if re.search(r"\{\{[A-Z_]+\}\}", open(path, encoding="utf-8").read()):
                    hits.append(os.path.relpath(path, root))
            except UnicodeDecodeError:
                pass
    return hits


def create(name, industry, slug=None, dest=None, author="Kevin Seyranoglu", github_user="KevinSeyranoglu",
           git=True, test=True):
    slug = slug or slugify(name)
    dest = os.path.expanduser(dest or os.path.dirname(KIT))
    target = os.path.join(dest, slug)
    if os.path.exists(target):
        raise SystemExit(f"{target} already exists: pick another --slug or --dest")
    shutil.copytree(STARTER, target, ignore=IGNORE)

    skills_out = os.path.join(target, ".claude", "skills")
    for skill in sorted(os.listdir(SKILLS)):
        if skill not in KIT_ONLY_SKILLS:
            shutil.copytree(os.path.join(SKILLS, skill), os.path.join(skills_out, skill), ignore=IGNORE)
    os.makedirs(os.path.join(target, "docs"), exist_ok=True)
    shutil.copy(os.path.join(KIT, "PLAYBOOK.md"), os.path.join(target, "docs", "PLAYBOOK.md"))
    brief = os.path.join(KIT, "briefs", f"{slug}.md")
    if os.path.exists(brief):
        shutil.copy(brief, os.path.join(target, "docs", "BRIEF.md"))

    fill(target, {"COMPANY_NAME": name, "INDUSTRY": industry, "SLUG": slug, "AUTHOR": author,
                  "GITHUB_USER": github_user, "YEAR": str(datetime.date.today().year)})
    left = leftovers(target)
    if left:
        raise SystemExit(f"unfilled placeholders in: {', '.join(left)}")

    if git:
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=target, check=True)
    if test:
        r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
                           cwd=target, capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr)
        if r.returncode:
            raise SystemExit(f"starter tests failed in {target}:\n{r.stdout[-3000:]}")
    return target


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("name", help='fictional company name, e.g. "Maple Ridge Bakery"')
    ap.add_argument("--industry", required=True, help='short phrase, e.g. "industrial bakery"')
    ap.add_argument("--slug", help="repo/folder name (default: from the name)")
    ap.add_argument("--dest", help="parent folder (default: next to the kit)")
    ap.add_argument("--author", default="Kevin Seyranoglu")
    ap.add_argument("--github-user", default="KevinSeyranoglu")
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--no-test", action="store_true", help="skip running the starter tests")
    a = ap.parse_args(argv)
    target = create(a.name, a.industry, a.slug, a.dest, a.author, a.github_user, not a.no_git, not a.no_test)
    print(f"\nCreated {target}\n\nNext: open that folder in Claude Code and ask it to write the spec "
          f"(company-spec skill).\nTo publish: cd {target} && gh repo create {os.path.basename(target)} "
          f"--public --source . --push")


if __name__ == "__main__":
    main()
