# warp-common-skills-as-plugin

A fork of [`warpdotdev/common-skills`](https://github.com/warpdotdev/common-skills)
packaged as a Claude Code plugin marketplace. Upstream ships its skills through the
`skills` npm CLI. This fork exposes the same `.agents/skills/` as installable Claude
Code plugins and keeps them synced.

## Install

```sh
/plugin marketplace add UkrainianCitizen/warp-common-skills-as-plugin
```

Then install one or more bundles:

```sh
/plugin install warp-engineering-pocockless@warp-common-skills
/plugin install warp-productivity-pocockless@warp-common-skills
/plugin install warp-misc@warp-common-skills
```

## Bundles

Claude Code enables or disables whole plugins, not individual skills, so the skills
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

Use the `/plugin` menu, or:

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

`scripts/generate_claude_plugins.py` copies skills into `plugins/` and writes
`.claude-plugin/marketplace.json`. The `CATEGORIES` dict in that script is the
hand-maintained skill-to-bundle mapping. A newly synced skill that is not listed
there lands in `warp-all` only and prints a warning.

`.github/workflows/regenerate-claude-plugins.yml` reruns the generator and commits
whenever `.agents/skills/` or the generator changes on `main`.

Do not hand-edit `plugins/` or `.claude-plugin/marketplace.json`. They are generated.
Edit the generator or the skills instead.

For skill authoring conventions and the upstream contribution process, see the
[upstream README](https://github.com/warpdotdev/common-skills#readme).
