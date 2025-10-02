### To migrate a repository from Bitbucket to GitHub


To migrate a repository from Bitbucket to GitHub while preserving commit history, branches, and tags, follow these steps:


1. Clone the Bitbucket Repository Locally

```bash
git clone --mirror https://bitbucket.org/your-team/your-repo.git
cd your-repo.git
```

2. Create a New Repository on GitHub


-	Go to GitHub and create a new repository.
-	Do NOT initialize it with a README or .gitignore.


3. Add GitHub as a New Remote

```bash
git remote set-url --push origin https://github.com/your-username/your-repo.git
```

4. Push Everything to GitHub

```bash
git push --mirror
```
-	This pushes all branches, tags, and commit history to GitHub.


5. Verify the Migration

-	Go to your GitHub repository and check if:
    -	Branches are present (git branch -r)
    -	Tags are present (git tag)
    -	Commit history is intact (git log)


1. Update Local Clones

If your team has local clones of the Bitbucket repository, they need to update their remotes:

```bash
git remote set-url origin https://github.com/your-username/your-repo.git
```

7. (Optional) Remove Bitbucket Remote

If you no longer need Bitbucket, you can remove its remote:

```bash
git remote remove bitbucket
```


8. Alternative: Using GitHub Import Tool

-	GitHub provides an import tool for easier migration.
-	Go to your new GitHub repository → “Import repository”.
-	Provide your Bitbucket repository URL and follow the steps.


9. 🎯 Final Notes:
    
-	If the repository is large, GitHub may enforce rate limits—consider pushing branches separately.
-	If using SSH authentication, replace HTTPS URLs with SSH:

```bash
git remote set-url --push origin git@github.com:your-username/your-repo.git
```
-	If your Bitbucket repository contains LFS-tracked files, install Git LFS before migrating.

This ensures a smooth and complete migration to GitHub 🚀.


