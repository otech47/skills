# skills

Agent skills, one directory per skill under `skills/`.

## What's here

- [`visual-report`](skills/visual-report): turns a long answer into a self-contained HTML report that opens with the big picture and buries the detail.
- [`skill-creator`](skills/skill-creator): create new skills, edit and improve existing ones, and measure skill performance with evals and description optimization.

## Using a skill

Symlink it into wherever your agent looks for skills:

```bash
ln -s "$PWD/skills/visual-report" ~/.claude/skills/visual-report
```

A skill is a directory with a `SKILL.md` at its root, plus whatever `assets/`, `references/`, and `scripts/` it needs.
