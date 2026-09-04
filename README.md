# warp-common-skills-as-plugin

A fork of [`warpdotdev/common-skills`](https://github.com/warpdotdev/common-skills)
packaged as a multi-tool plugin marketplace: Claude Code, Cursor, and (via the raw
skill tree) Codex. Upstream ships its skills through the `skills` npm CLI. This fork
exposes the same `.agents/skills/` as installable plugins and keeps them synced.

## Install

### Claude Code

```sh
/plugin marketplace add UkrainianCitizen/warp-common-skills-as-plugin
/plugin install warp-engineering-pocockless@warp-common-skills
/plugin install warp-productivity-pocockless@warp-common-skills
/plugin install warp-misc@warp-common-skills
```

### Cursor

Use the marketplace "Import from Repo" flow with this repository URL, or point it
at one bundle directly, e.g. `plugins/warp-engineering-pocockless`. Each plugin
carries a native `.cursor-plugin/plugin.json`, and the repo root has a
`.cursor-plugin/marketplace.json` listing every bundle.

### Codex

Codex reads skills straight out of an `.agents/skills/` directory, no plugin
wrapper needed. Either clone this repo and point Codex at it, or copy the skill
directories you want into your own `~/.agents/skills` or `<repo>/.agents/skills`.
Each bundle also ships an [Agent Plugins 1.0](https://agent-plugins.org) `plugin.json`
at its root (`plugins/<bundle>/plugin.json`) for any Codex flow that consumes that
open standard directly — this fork has not been able to confirm Codex's exact
marketplace/registry mechanism, so treat that path as best-effort.

## Bundles

These tools enable or disable whole plugins, not individual skills, so the skills
are grouped into a few bundles. Every plugin name is prefixed `warp-`.

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
own `SKILL.md` frontmatter, which is what Claude Code reads to decide when to trigger
it.

`scripts/generate_claude_plugins.py` copies skills into `plugins/<bundle>/skills/`
and writes, per bundle, a `.claude-plugin/plugin.json`, a `.cursor-plugin/plugin.json`,
and a root `plugin.json` (Agent Plugins 1.0). At the repo root it writes
`.claude-plugin/marketplace.json` and `.cursor-plugin/marketplace.json`. The
`CATEGORIES` dict in that script is the hand-maintained skill-to-bundle mapping. A
newly synced skill that is not listed there lands in `warp-all` only and prints a
warning.

`.github/workflows/regenerate-claude-plugins.yml` reruns the generator and commits
whenever `.agents/skills/` or the generator changes on `main`.

Do not hand-edit anything under `plugins/`, `.claude-plugin/`, or `.cursor-plugin/`.
They are generated. Edit the generator or the skills instead.

For skill authoring conventions and the upstream contribution process, see the
[upstream README](https://github.com/warpdotdev/common-skills#readme).
