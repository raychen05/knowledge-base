## GitHub - Best Practices


### 🧾 1. Commit Message Guidelines


✅ Format:

```vbnet
<type>: <short summary in present tense>
[optional body with motivation / context]
[optional footer with issue reference]
```

✅ Common Commit Types:

| **Type**        | **Use For**                                                    |
|-----------------|---------------------------------------------------------------|
| **feat**        | New features                                                   |
| **fix**         | Bug fixes                                                      |
| **refactor**    | Code refactoring (no feature or bug fix)                       |
| **docs**        | Documentation changes                                          |
| **test**        | Adding or fixing tests                                         |
| **chore**       | Non-functional updates (e.g., build config)                    |
| **perf**        | Performance improvements                                        |
| **ci**          | CI/CD pipeline changes                                          |



✅ Examples:


```bash

feat: add search API endpoint for user profiles

fix: correct off-by-one error in ranking algorithm

docs: update README with authentication details

chore: upgrade dependencies to latest stable versions
```


### 🌿 2. Branching Strategy

* Use a feature-based branching model:bashmain
* └── feature/my-new-feature
* └── fix/typo-in-doc
* └── chore/upgrade-deps
* 
* Always branch off main or dev, depending on your release flow.
* Optional: adopt Git Flow or GitHub Flow depending on team size and deployment cycle.


✅ Recommended Branch Types:

| **Branch**      | **Purpose**                                                        |
|-----------------|--------------------------------------------------------------------|
| **main**        | Always reflects production-ready code                             |
| **dev**         | Integrated code from all features; for QA/CI                       |
| **feature/***   | Individual features or stories                                     |
| **fix/***       | Hotfixes or bug fixes                                             |
| **release/***   | (Optional) Pre-release testing / staging                           |
| **hotfix/***    | Emergency fixes branched directly from main                        |



### 🔁 2. Workflow Example

```bash
# 1. Start from dev
git checkout dev

# 2. Create feature branch
git checkout -b feature/add-login-api

# 3. Work locally, push to GitHub
git push origin feature/add-login-api

# 4. Create PR -> dev
# 5. Merge after review and tests pass
```

### 🔄 Release Cycle:

1. Merge dev → release/x.y.z (optional staging)
2. Tag version: v1.2.0
3. Merge release/x.y.z → main
4. Deploy from main
5. Tag the release in GitHub


### 🚀 3. Release Versioning (SemVer)

Follow Semantic Versioning (SemVer):

vMAJOR.MINOR.PATCH  
e.g., v1.2.3

| **Version Type** | **When to bump**                                  |
|------------------|---------------------------------------------------|
| **MAJOR**        | Breaking changes                                  |
| **MINOR**        | New features, backward-compatible                 |
| **PATCH**        | Bug fixes only                                    |



✅ Tags Example

```bash

git tag v1.3.0
git push origin v1.3.0

```

Use GitHub Releases to publish release notes with artifacts if needed.


### 🔒 4. Branch Protections (Highly Recommended)

Apply these to main and optionally dev:

* ✅ Require PRs before merging
* ✅ Require status checks (CI) to pass
* ✅ Require code review approvals
* ✅ Restrict force pushes and direct pushes
* ✅ Use signed commits (if needed)


### 🧹 5. Clean-up & Maintenance

* Delete feature branches after merge
* Keep main and dev up to date
* Tag and document every release
* Monitor dependencies using GitHub Dependabot


### 📦 6. Automation Tools

| **Tool**                 | **Use Case**                                          |
|--------------------------|-------------------------------------------------------|
| **GitHub Actions**        | Automate builds, tests, deployments                   |
| **Semantic Release**      | Auto bump version + changelog from PRs                |
| **Husky + Lint-staged**   | Prevent bad commits                                   |
| **Commitlint**            | Enforce commit message standards                      |
| **Renovate / Dependabot** | Auto-update dependencies                               |


### 📝 Example Version Control Policy

| **Step**            | **Action**                                                   |
|---------------------|--------------------------------------------------------------|
| **Developer starts** | Branches from dev using feature/*                            |
| **Daily integration**| Merges to dev, tested via CI                                 |
| **Pre-release**      | Create release/1.3.0, freeze changes                         |
| **QA sign-off**      | Merge to main, tag v1.3.0, deploy                            |
| **Hotfix needed**    | Branch hotfix/* from main, PR back to main and dev           |


✅ Summary Checklist

| **Task**               | **Best Practice**                                         |
|------------------------|-----------------------------------------------------------|
| **Branch naming**      | Use feature/, fix/, etc.                                  |
| **Release tags**       | Follow SemVer (v1.0.0)                                    |
| **CI/CD integration**  | Automate tests and builds                                 |
| **PR policies**        | Use required reviews/checks                               |
| **Deployment from**    | main branch only                                           |
| **Branch cleanup**     | Delete after merge                                         |




### 🚀 3. Pull Request (PR) Best Practices

✅ Title:

* Clear and concise:sqlfeat: add caching layer for search results
* fix: handle null pointer in author lookup


✅ Description:

* What was changed and why
* Screenshots or logs (for UI/backend)
* Related Jira ticket / issue number
* Checklist of validations or tasks


✅ Example PR Description:

```markdown

### Summary
- Adds Redis caching layer to improve response time for `/search`
- TTL is configurable via environment variable

### Related
- JIRA: AGRA-1234

### Checklist
- [x] Unit tests added
- [x] Integration tested on dev
- [x] Reviewed by backend team
```


### 👥 4. Code Review Etiquette


As a Contributor:

* Ensure tests pass and code is linted
* Keep PRs focused and small if possible
* Tag appropriate reviewers
* Be open to feedback, avoid being defensive

As a Reviewer:

* Be constructive and kind
* Focus on correctness, readability, maintainability
* Use suggestions where possible:suggestionConsider renaming this to `normalizedScore` for clarity.
* 

### ✅ 5. General GitHub Hygiene


| **Practice**                    | **Tip**                                                             |
|----------------------------------|---------------------------------------------------------------------|
| ✅ **Small commits**             | Easier to review and revert                                         |
| ✅ **Rebase / squash if needed** | Keeps history clean (avoid noisy commit logs)                       |
| ✅ **Delete merged branches**    | Prevents clutter                                                     |
| ✅ **Use .gitignore**            | Avoid committing secrets, large files, temp files                   |
| ✅ **Use draft PRs**             | When you're still working but want early feedback                   |
| ✅ **Protect main branch**       | Require PRs, reviews, and passing checks                            |
| ✅ **Use PR templates**          | Enforce structure and checklist                                     |
| ✅ **Sign commits (optional)**   | For verifying authorship in high-trust environments                 |



### 🔐 6. Security & Compliance

* Use GitHub secrets for tokens, not in code
* Run security scanners in CI:
    * GitHub Advanced Security
    * Semgrep
    * Dependabot
* Avoid committing:
    * .env files
    * AWS credentials
    * Private keys


🧰 Tools to Help

| **Tool**               | **Use Case**                                          |
|------------------------|-------------------------------------------------------|
| **Husky + lint-staged** | Pre-commit checks (lint, format)                     |
| **Commitlint**          | Enforce conventional commits                         |
| **Semantic PRs**        | Auto versioning, changelogs                          |
| **GitHub Actions**      | Automate CI/CD, scans, tests                         |



