# Four-person GitHub workflow

1. Clone the single shared repository. Everyone works on their own feature branch:
   `git switch -c feat/data-crops` or `feat/controlnet`, `feat/ic-light`, `feat/baseline-eval`.
2. Run `git pull --ff-only origin main` while on `main` before creating a fresh branch.
3. Write code only in your owned files unless coordinated with another owner.
4. Test your work, document your experiment parameters, then:
   `git add src/...` (or your owned notebook), `git commit -m "..."`, `git push -u origin <branch>`.
5. Open a GitHub pull request into main; ask one teammate to review; merge only when tests and input/output filenames align.
6. After merge, teammates on main run `git pull origin main`.
7. Never commit Google Street View downloads, large weights, credentials or private keys.
8. Everyone reports: done, blocker, next action at daily 10-minute standups.

Suggested first check-in branches: `feat/data-crops`, `feat/controlnet`, `feat/ic-light`, `feat/baseline-eval`.
