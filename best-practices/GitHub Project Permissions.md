
## GitHub Project Permissions: Best Practices

Managing GitHub project permissions is crucial for security, collaboration, and auditability. Here are key best practices:

### 1. Use Teams and Roles

- Organize users into GitHub Teams (e.g., Developers, Reviewers, Admins).
- Assign repository access at the team level, not individually.
- This streamlines onboarding/offboarding and maintains consistency.

### 2. Principle of Least Privilege

- Grant only the permissions necessary for each role:
    - **Read**: Stakeholders, QA.
    - **Triage**: Manage issues/PRs, no code pushes.
    - **Write**: Developers who push code.
    - **Maintain**: Leads who manage settings.
    - **Admin**: Reserved for trusted maintainers.

### 3. Enforce Branch Protection

- Protect main/production branches:
    - Require PR reviews and passing status checks.
    - Restrict force pushes and deletions.
    - Optionally require signed commits.

### 4. Organization-Level Security

- Enable 2FA for all members.
- Restrict repository creation to admins.
- Regularly audit and remove stale outside collaborators.

### 5. Code Owners & Review Policies

- Use a `CODEOWNERS` file to auto-request reviews from the right teams.
- Ensures critical code is reviewed by appropriate members.

### 6. Automate Access Management

- Integrate GitHub Teams with SSO (e.g., Azure AD, Okta).
- Use scripts or GitHub Actions to audit permissions regularly.

### 7. Monitor and Audit

- Periodically review admin/write access and tokens/keys.
- Use GitHub’s audit log or third-party tools for monitoring.

---

### Example Role Matrix

| Role         | Permissions | Typical Members         |
|--------------|-------------|------------------------|
| **Admin**    | Admin       | Tech Leads, DevOps     |
| **Maintainer** | Maintain  | Senior Engineers       |
| **Developer**  | Write     | Engineers              |
| **Reviewer**   | Triage    | QA, Reviewers          |
| **Viewer**     | Read      | PMs, Analysts          |

---

### Permission Management Guidance

- Limit “Admin” access to a few maintainers.
- Admins can change protection rules, secrets, collaborators, and repo visibility.
- Recommended: 
    - Create teams like `project-admins` (few leads) and `project-devs` (Write/Maintain).
    - Only admins create repos; developers push/branch as needed.
- For frequent repo creation:
    - Let devs create in personal namespace, then transfer after review.
    - Or use a sandbox org for prototyping.
- Always enforce branch protection and audit access regularly.

---

### Example Workflow for Repository Creation and Transfer

**Step 1:** Developer creates repo under personal account.

**Step 2:** Develop and review. Invite collaborators as needed.

**Step 3:** Transfer repo to organization:
    - Go to Settings → General → Danger Zone → Transfer ownership.
    - Enter org and repo name to confirm.
    - Admins may need to approve.

**Step 4:** Admins configure permissions, protection rules, CI/CD, and secrets.

**Step 5:** Team continues collaborative development.

---

**Summary Table**

| Step | Who        | Action                                 |
|------|------------|----------------------------------------|
| 1    | Developer  | Create repo under personal account     |
| 2    | Developer  | Build, test, peer review               |
| 3    | Developer  | Request transfer to organization       |
| 4    | Admin      | Approve transfer, apply policies       |
| 5    | Team       | Continue collaborative development     |

