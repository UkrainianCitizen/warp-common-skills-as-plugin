#!/usr/bin/env python3
"""Generate multi-tool plugin + marketplace files from .agents/skills/.

Emits a small set of curated bundle plugins instead of one plugin per skill:

  warp-engineering              all dev-workflow skills
  warp-engineering-pocockless   ^ minus skills that overlap mattpocock-skills
  warp-productivity             research / output / thinking skills
  warp-productivity-pocockless  ^ minus skills that overlap mattpocock-skills
  warp-misc                     meta / branding / internal-feedback skills
  warp-all                      every skill in the repo, categorized or not

Each plugin directory ships three manifests pointing at the same skills/ copy:

  .claude-plugin/plugin.json   Claude Code
  .cursor-plugin/plugin.json   Cursor's native format
  plugin.json                  Agent Plugins 1.0 (the open standard Cursor and
                                Codex both read; also the fallback for any tool
                                that implements the open spec)

...and two marketplace/registry files at the repo root:

  .claude-plugin/marketplace.json   Claude Code (`/plugin marketplace add`)
  .cursor-plugin/marketplace.json   Cursor (`Import from Repo`)

Codex reads skills straight out of .agents/skills/ without a plugin wrapper,
so no Codex-specific registry file is generated - see README.

Skill content is copied from .agents/skills/ - that stays the source of truth
and this script is re-run after every upstream sync. CATEGORIES is maintained
by hand; a skill missing from it lands only in warp-all and prints a warning.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_SRC = REPO / ".agents" / "skills"
PLUGINS_DIR = REPO / "plugins"
CLAUDE_MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
CURSOR_MARKETPLACE = REPO / ".cursor-plugin" / "marketplace.json"

MARKETPLACE_NAME = "warp-common-skills"
OWNER = {"name": "UkrainianCitizen"}
AUTHOR = {"name": "UkrainianCitizen"}
VERSION = "0.1.0"
AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
BUNDLE_ALL = "warp-all"

# Hand-maintained. Every skill dir in .agents/skills/ should appear in exactly
# one list here. scan-new-specs is deliberately omitted (retired upstream) and
# reaches users only through warp-all.
CATEGORIES: dict[str, list[str]] = {
    "warp-engineering": [
        "check-impl-against-spec",
        "create-pr",
        "diagnose-ci-failures",
        "fix-errors",
        "implement-specs",
        "pr-walkthrough",
        "reproduce-bug-report",
        "resolve-merge-conflicts",
        "respond-to-pr-comments-in-blocklist",
        "review-pr",
        "saga",
        "spec-driven-implementation",
        "validate-changes-match-specs",
        "write-feature-docs",
        "write-pr-description",
        "write-product-spec",
        "write-tech-spec",
    ],
    "warp-productivity": [
        "research",
        "readout",
        "council",
        "cross-critique",
    ],
    "warp-misc": [
        "brandalf",
        "complain",
        "suggestion-box",
        "skill-doctor",
        "update-skill",
    ],
}

# name -> (base category, skills to drop because mattpocock-skills covers them)
POCOCKLESS: dict[str, tuple[str, set[str]]] = {
    "warp-engineering-pocockless": (
        "warp-engineering",
        {
            "resolve-merge-conflicts",
            "review-pr",
            "check-impl-against-spec",
            "validate-changes-match-specs",
        },
    ),
    "warp-productivity-pocockless": (
        "warp-productivity",
        {"research"},
    ),
}

DESCRIPTIONS: dict[str, str] = {
    "warp-engineering": "All Warp dev-workflow skills: specs, PRs, CI triage, merge conflicts, autonomous implementation.",
    "warp-engineering-pocockless": "warp-engineering minus skills that overlap mattpocock-skills (code-review, resolving-merge-conflicts).",
    "warp-productivity": "Research, readout documents, and multi-agent council/critique skills.",
    "warp-productivity-pocockless": "warp-productivity minus the research skill, which overlaps mattpocock-skills.",
    "warp-misc": "Meta and internal skills: brand assets, skill authoring, skill-doctor, agent feedback channels.",
    BUNDLE_ALL: "Every skill in this fork of warpdotdev/common-skills, in one plugin.",
}


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    block = text[3:end]
    out: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            out[key] = val.strip()
        elif key and line.strip():
            out[key] += " " + line.strip()
    return out


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def copy_skill(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def build_plugin(name: str, skill_names: list[str], all_skill_dirs: dict[str, Path]) -> dict:
    plugin_dir = PLUGINS_DIR / name
    dst_skills = plugin_dir / "skills"
    for skill in skill_names:
        copy_skill(all_skill_dirs[skill], dst_skills / skill)
    desc = DESCRIPTIONS.get(name, f"{name} skills.")

    # Claude Code
    write_json(
        plugin_dir / ".claude-plugin" / "plugin.json",
        {"name": name, "version": VERSION, "description": desc, "author": AUTHOR},
    )
    # Cursor's native format
    write_json(
        plugin_dir / ".cursor-plugin" / "plugin.json",
        {"name": name, "version": VERSION, "description": desc, "author": AUTHOR},
    )
    # Agent Plugins 1.0 (open standard: Cursor + Codex)
    write_json(
        plugin_dir / "plugin.json",
        {
            "$schema": AGENT_PLUGINS_SCHEMA,
            "name": name,
            "description": desc,
            "version": VERSION,
            "author": AUTHOR,
        },
    )

    return {"name": name, "source": f"./plugins/{name}", "description": desc, "version": VERSION}


def main() -> None:
    all_skill_dirs = {
        p.name: p for p in sorted(SKILLS_SRC.iterdir()) if (p / "SKILL.md").is_file()
    }

    categorized = {s for names in CATEGORIES.values() for s in names}
    missing = categorized - all_skill_dirs.keys()
    if missing:
        sys.exit(f"CATEGORIES references skills not in {SKILLS_SRC}: {sorted(missing)}")

    uncategorized = sorted(all_skill_dirs.keys() - categorized - {"scan-new-specs"})
    if uncategorized:
        print(f"WARNING: uncategorized skills (warp-all only): {uncategorized}")

    if PLUGINS_DIR.exists():
        shutil.rmtree(PLUGINS_DIR)

    entries: list[dict] = []

    for name, skill_names in CATEGORIES.items():
        entries.append(build_plugin(name, sorted(skill_names), all_skill_dirs))

    for name, (base, drop) in POCOCKLESS.items():
        skill_names = [s for s in CATEGORIES[base] if s not in drop]
        entries.append(build_plugin(name, sorted(skill_names), all_skill_dirs))

    entries.append(build_plugin(BUNDLE_ALL, sorted(all_skill_dirs.keys()), all_skill_dirs))

    marketplace_description = (
        "Fork of warpdotdev/common-skills packaged as a multi-tool plugin marketplace: "
        "curated bundle plugins (engineering, productivity, misc), pocockless variants "
        "that drop skills overlapping mattpocock-skills, and warp-all."
    )
    write_json(
        CLAUDE_MARKETPLACE,
        {
            "name": MARKETPLACE_NAME,
            "owner": OWNER,
            "metadata": {"description": marketplace_description, "version": VERSION},
            "plugins": entries,
        },
    )
    write_json(
        CURSOR_MARKETPLACE,
        {
            "name": MARKETPLACE_NAME,
            "owner": OWNER,
            "description": marketplace_description,
            "version": VERSION,
            "plugins": entries,
        },
    )
    print(f"Generated {len(entries)} plugins from {len(all_skill_dirs)} skills.")


if __name__ == "__main__":
    main()
