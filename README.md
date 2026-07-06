# deepeval-tracer

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
