"""Regenerate every skill README, the catalog table in the root README and docs/catalog.js
from catalog.json. Run after adding or editing a skill:  python tools/build_catalog.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
REPO = CAT["repo"]
RAW = f"https://raw.githubusercontent.com/{REPO}/main"
LABEL = {c["id"]: c["label"] for c in CAT["categories"]}
BEGIN, END = "<!-- catalog:begin -->", "<!-- catalog:end -->"


def cmds(name):
    return {
        "mac": f"curl -fsSL {RAW}/install.sh | bash -s -- {name}",
        "win": f"& ([scriptblock]::Create((irm {RAW}/install.ps1))) {name}",
        "manual": f"Copy skills/{name}/ into ~/.claude/skills/{name}/",
    }


def files_of(name):
    base = ROOT / "skills" / name
    return sorted(p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file() and p.name != "README.md")


def skill_readme(s):
    c = cmds(s["name"])
    lines = [
        f"# {s['title']}",
        "",
        f"`{s['name']}` | {LABEL[s['category']]}",
        "",
        s["summary"],
        "",
        "| | |",
        "|---|---|",
        f"| **What** | {s['summary']} |",
        f"| **When** | {s['when']} |",
        f"| **Who it is for** | {s['for']} |",
        f"| **Needs** | {', '.join(s['needs'])} |",
        f"| **Customize** | {s['customize']} |",
    ]
    if s.get("conflicts"):
        lines.append(f"| **Pick one** | Do not install alongside `{'`, `'.join(s['conflicts'])}`. Both manage the same context hooks. |")
    if s.get("license"):
        lines.append(f"| **License** | {s['license']}. See SKILL.md for attribution. |")
    lines += [
        "",
        "## Install",
        "",
        "Mac or Linux:",
        "```bash",
        c["mac"],
        "```",
        "",
        "Windows PowerShell:",
        "```powershell",
        c["win"],
        "```",
        "",
        f"Or by hand: copy this `{s['name']}` folder into `~/.claude/skills/` so you have `~/.claude/skills/{s['name']}/SKILL.md`. On Windows `~` is your user folder (`%USERPROFILE%`). Then start a new Claude Code session.",
        "",
        "## Try it",
        "",
        f"> {s['try']}",
        "",
        "## Files",
        "",
    ]
    lines += [f"- `{f}`" for f in files_of(s["name"])]
    lines += ["", "Full instructions live in [SKILL.md](SKILL.md). Back to the [library](../../README.md).", ""]
    return "\n".join(lines)


def table():
    rows = ["| Skill | What it does | Who it is for | Install (Mac/Linux) |", "|---|---|---|---|"]
    for cat in CAT["categories"]:
        rows.append(f"| **{cat['label']}** | | | |")
        for s in [x for x in CAT["skills"] if x["category"] == cat["id"]]:
            star = " (start here)" if s.get("start_here") else ""
            rows.append(f"| [`{s['name']}`](skills/{s['name']}/){star} | {s['summary']} | {s['for']} | `./install.sh {s['name']}` |")
    return "\n".join(rows)


def main():
    for s in CAT["skills"]:
        (ROOT / "skills" / s["name"] / "README.md").write_text(skill_readme(s), encoding="utf-8", newline="\n")
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    a, b = text.index(BEGIN) + len(BEGIN), text.index(END)
    readme.write_text(text[:a] + "\n" + table() + "\n" + text[b:], encoding="utf-8", newline="\n")
    data = dict(CAT)
    data["skills"] = [dict(s, files=files_of(s["name"]), install=cmds(s["name"])) for s in CAT["skills"]]
    (ROOT / "docs" / "catalog.js").write_text("window.SKILLS_CATALOG = " + json.dumps(data, indent=1) + ";\n", encoding="utf-8", newline="\n")
    print(f"built {len(CAT['skills'])} skill READMEs, README table, docs/catalog.js")


if __name__ == "__main__":
    main()
