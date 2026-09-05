# warp-common-skills-as-plugin

A fork of [`warpdotdev/common-skills`](https://github.com/warpdotdev/common-skills)
packaged as installable plugins for Claude Code, Codex, and Cursor. Upstream ships
its skills through the `skills` npm CLI. This fork wraps the same `.agents/skills/`
in per-tool plugin manifests and keeps them synced.

## Install

### Claude Code

```sh
/plugin marketplace add UkrainianCitizen/warp-common-skills-as-plugin
/plugin install warp-engineering-pocockless@warp-common-skills
/plugin install warp-productivity-pocockless@warp-common-skills
/plugin install warp-misc@warp-common-skills
```

### Codex

Each bundle has a `.codex-plugin/plugin.json` manifest pointing at its `skills/`
directory. Install a bundle by pointing Codex at `plugins/<bundle>/`, e.g.
`plugins/warp-engineering-pocockless`. Codex documents no marketplace schema, so
there is no repo-level registry to add.

### Cursor

Cursor has no native `SKILL.md` reader, so each skill is mirrored as a
`.cursor/rules/<skill>.mdc` rule under its bundle. Copy the bundle's
`.cursor/rules/` directory into your project's `.cursor/rules/`, or copy the
individual `.mdc` files you want. Each rule uses "Apply Intelligently" with the
skill's own description as the trigger.

## Bundles

Claude Code and Codex enable or disable whole plugins, not individual skills, so
the skills are grouped into a few bundles. Every plugin name is prefixed `warp-`.
(Cursor rules are per skill, so a Cursor user can also just take individual
`.mdc` files.)

| Plugin | Skills |
|---|---|
| `warp-engineering` | `check-impl-against-spec`, `create-pr`, `diagnose-ci-failures`, `fix-errors`, `implement-specs`, `pr-walkthrough`, `reproduce-bug-report`, `resolve-merge-conflicts`, `respond-to-pr-comments-in-blocklist`, `review-pr`, `saga`, `spec-driven-implementation`, `validate-changes-match-specs`, `write-feature-docs`, `write-pr-description`, `write-product-spec`, `write-tech-spec` |
| `warp-engineering-pocockless` | `warp-engineering` minus `resolve-merge-conflicts`, `review-pr`, `check-impl-against-spec`, `validate-changes-match-specs` |
| `warp-productivity` | `research`, `readout`, `council`, `cross-critique` |
| `warp-productivity-pocockless` | `warp-productivity` minus `research` |
| `warp-misc` | `brandalf`, `complain`, `suggestion-box`, `skill-doctor`, `update-skill` |
| `warp-all` | every skill in the repo, including the retired `scan-new-specs` |

### `-pocockless` variants

Use these if you already run [`mattpocock-skills`](https://github.com/mattpocock/skills).
They drop Warp skills that overlap Matt's (`code-review`, `resolving-merge-conflicts`,
`research`) so two skills don't compete to trigger for the same task.

## Enable / disable

In Claude Code, use the `/plugin` menu, or:

```sh
claude plugin disable warp-misc
claude plugin enable warp-misc
```

## Sync updates

```sh
/plugin marketplace update
```

`.github/workflows/sync-upstream.yml` merges `warpdotdev/common-skills` `main` into
this fork daily, and on manual `workflow_dispatch`. It regenerates the plugin files
and pushes. To sync on demand, run that workflow from the Actions tab, or locally:

```sh
git remote add upstream https://github.com/warpdotdev/common-skills.git  # once
git fetch upstream main && git merge upstream/main
python3 scripts/generate_claude_plugins.py
git push
```

## How the packaging works

`.agents/skills/` is the source of truth, synced from upstream. Each skill keeps its
own `SKILL.md` with a `description` in the frontmatter, which is the trigger every
tool uses to decide when to invoke it.

`scripts/generate_claude_plugins.py` builds each `plugins/<bundle>/` with:

- `skills/<skill>/` copied from `.agents/skills/`
- `.claude-plugin/plugin.json` (Claude Code)
- `.codex-plugin/plugin.json` (Codex)
- `.cursor/rules/<skill>.mdc` per skill (Cursor): frontmatter `description` copied
  from the skill, body copied from the skill's instructions

At the repo root it writes `.claude-plugin/marketplace.json`. The `CATEGORIES` dict
in the script is the hand-maintained skill-to-bundle mapping. A newly synced skill
not listed there lands in `warp-all` only and prints a warning.

`.github/workflows/regenerate-claude-plugins.yml` reruns the generator and commits
whenever `.agents/skills/` or the generator changes on `main`.

Do not hand-edit anything under `plugins/` or `.claude-plugin/`. They are generated.
Edit the generator or the skills instead. The manifest formats and their sources are
documented in `major-ai-plugin-creation.md` in the parent projects directory (local,
not in this repo).

For skill authoring conventions and the upstream contribution process, see the
[upstream README](https://github.com/warpdotdev/common-skills#readme).
