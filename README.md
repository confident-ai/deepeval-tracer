# deepeval-actions

The automation behind Confident AI's one-click tracing setup. When you connect a
repository during onboarding, it opens a pull request that adds
[deepeval](https://github.com/confident-ai/deepeval) tracing to your app — so you can
start seeing traces in Confident AI without instrumenting anything by hand.

## What it does

When you connect your repo, this automation:

1. Accesses it with a **short-lived token scoped to just that one repository**.
2. Detects your framework and model setup and adds deepeval tracing — a native
   integration where one exists, or the `@observe` decorator otherwise.
3. Opens a **pull request** with the change for you to review and merge.

Your code is processed only for the duration of that run and is **never stored**, and
nothing is added to your repository except the pull request.

## Run it on your own repo (self-serve)

Prefer to run it yourself instead of the hosted onboarding flow? This repo also ships a
self-serve workflow, `add-tracing.md`, that runs the same agent against **your** repo and
opens a tracing PR — no GitHub App and no callback, just the built-in `GITHUB_TOKEN`. All
you need is [`gh-aw`](https://github.com/github/gh-aw) and an `ANTHROPIC_API_KEY`; it runs
on GitHub Actions.

```bash
gh extension install github/gh-aw
gh aw add https://github.com/confident-ai/deepeval-actions/blob/main/.github/workflows/add-tracing.md
gh aw secrets set ANTHROPIC_API_KEY --value "sk-ant-..."
gh aw run add-tracing
```

Or try it against your repo in a throwaway sandbox first (nothing installed, no changes made):

```bash
gh aw trial https://github.com/confident-ai/deepeval-actions/blob/main/.github/workflows/add-tracing.md --clone-repo your-org/your-repo --dry-run
```
