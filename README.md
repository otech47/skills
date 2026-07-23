# skills

Agent skills, one directory per skill under `skills/`.

## What's here

- [`skills/visual-report`](skills/visual-report): turns a long structured answer into a self-contained local HTML report, ordered so the reader meets the big picture and a diagram first and the technical detail last.

## Using a skill

Copy the skill directory into wherever your agent looks for skills, or symlink it:

```bash
ln -s "$PWD/skills/visual-report" ~/.claude/skills/visual-report
```

Each skill is a directory holding a `SKILL.md` with frontmatter (`name`, `description`) plus any `assets/`, `references/`, and `scripts/` it needs.
