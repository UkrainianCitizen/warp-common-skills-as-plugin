# Common Skills

This repository is where common agent skills that should be shared across repositories go.

A skill belongs here when it captures a reusable workflow, convention, or operating procedure that is useful in more than one repository. Repository-specific skills should stay with the repository they apply to unless they can be generalized without losing important context.

## Repository layout

```text
.agents/
  skills/
    <skill-name>/
      SKILL.md
      scripts/      # optional helper scripts
      references/   # optional supporting docs
      assets/       # optional bundled assets
```

Each skill lives in its own directory under `.agents/skills/`. The only required file for a skill is `SKILL.md` with YAML frontmatter containing at least:

- `name`: the kebab-case skill identifier
- `description`: what the skill does and when agents should use it

## Current skills

### Spec workflow

- `write-product-spec` — writes user-facing `PRODUCT.md` specs.
- `write-tech-spec` — writes implementation-oriented `TECH.md` specs.
- `spec-driven-implementation` — guides the full spec-first workflow for substantial features.
- `implement-specs` — implements approved `PRODUCT.md` and `TECH.md` files while keeping specs and code aligned.

### Development workflow

- `create-pr` — guidance for preparing and opening pull requests.
- `write-pr-description` — writes the PR body: template sections, plain-language prose, and reviewer guidance.
- `diagnose-ci-failures` — workflow for inspecting GitHub CI failures and producing a fix plan.
- `fix-errors` — guidance for fixing build, lint, formatting, and test failures.
- `resolve-merge-conflicts` — workflow and helper script for resolving git conflicts with compact context.
- `review-pr` — produces structured PR review feedback from local diff artifacts.
- `check-impl-against-spec` — compares PR implementation changes against provided spec context during review.

### Investigation and decision-making

- `research` — delegates low signal-to-noise-ratio research work to subagents and returns distilled, evidence-backed findings.
- `cross-critique` — sharpens contested decisions by having agents critique one another's independent proposals before synthesis.

### Skill authoring

- `update-skill` — guidance for creating and maintaining skill directories and `SKILL.md` files.
- `skill-doctor` — grades a repo's installed skills by scoring recent local agent conversations, then drafts the skill edits the evidence justifies.

## Adding a shared skill

When adding a skill to this repository:

1. Put it under `.agents/skills/<skill-name>/`.
2. Include a `SKILL.md` with clear frontmatter.
3. Keep the skill focused on a reusable workflow rather than one repository's private details.
4. Move large reference material into `references/` and helper automation into `scripts/`.
5. If copying from another repo, copy first, then generalize in a separate change so the provenance is easy to review.

## Generalizing repository-specific skills

Some skills copied here may still contain repository-specific examples, paths, commands, or assumptions. That is okay during initial migration, but shared skills should eventually be generalized by:

- replacing hard-coded repository names with placeholders or conditional guidance
- separating common workflow guidance from local repository conventions
- moving repo-specific overrides back into the repository that needs them
- keeping descriptions broad enough to trigger in multiple repositories, but specific enough to avoid unrelated tasks

## Use as a Claude Code plugin

This fork is also published as a Claude Code plugin marketplace. The marketplace
manifest (`.claude-plugin/marketplace.json`) and the `plugins/` tree are
**generated** from `.agents/skills/` by `scripts/generate_claude_plugins.py` and
regenerated in CI on every push to `main`. Do not edit them by hand.

Claude Code enables or disables whole plugins, not individual skills, so the
generator emits a few curated bundles:

| Plugin | Skills |
|---|---|
| `warp-engineering` | all dev-workflow skills (specs, PRs, CI triage, merge conflicts, `saga`) |
| `warp-engineering-pocockless` | `warp-engineering` minus skills that overlap [`mattpocock-skills`](https://github.com/mattpocock/skills) (`code-review`, `resolving-merge-conflicts`) |
| `warp-productivity` | `research`, `readout`, `council`, `cross-critique` |
| `warp-productivity-pocockless` | `warp-productivity` minus `research` (overlaps `mattpocock-skills`) |
| `warp-misc` | `brandalf`, `complain`, `suggestion-box`, `skill-doctor`, `update-skill` |
| `warp-all` | every skill in the repo |

Use a `*-pocockless` variant if you already run `mattpocock-skills` and don't want
two skills competing to trigger for the same task. `scan-new-specs` is retired
upstream and ships only in `warp-all`.

### Install

```sh
/plugin marketplace add UkrainianCitizen/warp-common-skills-as-plugin
/plugin install warp-engineering-pocockless@warp-common-skills
/plugin install warp-productivity-pocockless@warp-common-skills
/plugin install warp-misc@warp-common-skills
```

### Enable / disable

Use the `/plugin` menu, or:

```sh
claude plugin disable warp-misc
claude plugin enable warp-misc
```

### Sync updates

```sh
/plugin marketplace update
```

This pulls the latest `main`, including any skills synced from
`warpdotdev/common-skills` upstream. Background auto-update also covers it.

The `.github/workflows/sync-upstream.yml` workflow merges `warpdotdev/common-skills`
`main` into this fork daily (and on manual `workflow_dispatch`), regenerates the
plugin files, and pushes. To sync on demand, run the workflow from the Actions tab
or locally:

```sh
git remote add upstream https://github.com/warpdotdev/common-skills.git  # once
git fetch upstream main && git merge upstream/main
python3 scripts/generate_claude_plugins.py
git push
```

### Regenerate locally

After merging upstream skill changes into `.agents/skills/`:

```sh
python3 scripts/generate_claude_plugins.py
```

## Usage

Consumers can install the shared skills with the `skills` CLI.

List available skills:

```sh
npx skills@latest add warpdotdev/common-skills --list
```

Install all common skills for Warp globally:

```sh
npx skills@latest add warpdotdev/common-skills --skill '*' --agent warp --global
```

Install one skill:

```sh
npx skills@latest add warpdotdev/common-skills --skill write-tech-spec --agent warp --global
```

Update installed skills later:

```sh
npx skills@latest update --global --agent warp
```

You can also copy or sync selected directories from `.agents/skills/` into a repository's own `.agents/skills/` directory.

Prefer copying only the skills a repository actually needs. If a common skill needs repository-specific behavior, add a small local companion skill in that repository rather than forking the shared skill unless the change is useful everywhere.
