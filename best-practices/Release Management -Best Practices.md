## Release management - Best Practice


Below is a concise, end-to-end best-practice summary and workflow that ties together Git branching, versioning, parallel feature development, deployment, and Dev → UAT → Prod promotion. This is the recommended enterprise pattern for data platforms, Spark/Databricks pipelines, and services.

Executive Principles (Non-Negotiable)
1. Branches are mutable → for development
2. Tags are immutable → for releases
3. Promotion = redeploy the same version
4. Never promote by merging
5. Prod always runs a tag

---


### 1️⃣ Git Branching Model (Simple, Modern)

```css
main                → always releasable
feature/-           → parallel development
hotfix/-            → patch from prod tag
```


❌ No dev, uat, prod branches
❌ No long-lived release branches unless LTS is required

---

### 2️⃣ Parallel Feature Development (Dev)


Flow
```css
feature/A
feature/B
feature/C
```

**Rules**
- Each feature in its own branch
- Dev allows instability
- Fast iteration, no tags

**Dev Deployment**
- Deploy directly from branch
- Version = branch + commit SHA

```css
dev deployment:
  source: feature/A
  version: feature-A-abc123
```
- ✔ Supports parallel teams
- ✔ No release pollution

---

3️⃣ Feature Integration (Dev)

When features are ready:

```bash
git checkout main
git merge feature/A
git merge feature/B
```

- Integration testing in Dev
- Still no tags

---

### 4️⃣ Create a Release (Versioning)


Once main is validated:
```bash
git tag -a v2.3.0 -m "Release v2.3.0"
git push origin v2.3.0
```

**Version Rules**
- Semantic Versioning: vMAJOR.MINOR.PATCH
- Tag = release bundle
- Tag never changes

---

### 5️⃣ Deployment & Promotion Model (Critical)

✅ Correct Promotion Model

| Environment | What is deployed |
|-------------|------------------|
| Dev         | tag v2.3.0       |
| UAT         | tag v2.3.0       |
| Prod        | tag v2.3.0       |

- ✔ Same code
- ✔ Same artifact
- ✔ No drift

Promotion is redeployment, not merge

---


### 6️⃣ CI/CD Deployment Workflow

**Pipeline Input**

```yaml
environment: uat
git_ref: v2.3.0
```

**Pipeline Behavior**

1. Checkout tag
2. Build once (or reuse artifact)
3. Deploy to target env
4. Record version metadata

---

### 7️⃣ Rollback Strategy

**Scenario**
Prod issue found

**Action**
```bash
Redeploy v2.2.5
```

- ✔ No branch
- ✔ No code change
- ✔ Instant rollback

---

### 8️⃣ Hotfix Workflow

**Scenario**

Prod = v2.3.0, urgent bug

```bash
git checkout -b hotfix/v2.3.1 v2.3.0
# fix bug
git commit
git tag -a v2.3.1
git push origin v2.3.1
```

**Deploy**:
```yaml
Dev → UAT → Prod : v2.3.1
```

---

### 9️⃣ Environment Responsibilities
| Environment | Source | Stability |
|-------------|--------|-----------|
| Dev | Branch / Tag | Low |
| UAT | Tag | High |
| Prod | Tag | Highest |

---

### 🔟 What NOT to Do (Anti-Patterns)

- ❌ Deploy prod from main
- ❌ Rebuild per environment
- ❌ Environment branches
- ❌ Retagging releases
- ❌ Cherry-picking across envs

---

11️⃣ Visual Workflow (End-to-End)

```css
feature/A ─┐
feature/B ─┼─> main ── tag v2.3.0 ──► Dev ─► UAT ─► Prod
feature/C ─┘
```

**Hotfix**:

```bash
v2.3.0 ──► hotfix/v2.3.1 ──► tag v2.3.1 ──► Dev → UAT → Prod
```


Final Best-Practice Checklist

- ✅ Branch for development
- ✅ Tag for releases
- ✅ Deploy by tag
- ✅ Promote by redeploying
- ✅ Rollback by redeploying old tag
- ✅ Hotfix = branch from tag → new tag


If you want, I can next:
- Provide CI/CD YAML templates
- Map this to Databricks Bundles
- Add version metadata + audit tables
- Design multi-tenant Dev environments

Just tell me your CI/CD stack.


---

## Map this to Databricks Bundles


Below is a clean, production-grade mapping of the Git branching / tagging / promotion model to Databricks Asset Bundles, aligned with Databricks’ intended design and enterprise best practices.

This assumes:
- Databricks Asset Bundles (databricks.yml)
- CI/CD driven deployments
- Dev → UAT → Prod promotion
- Parallel feature development

---

### 1️⃣ Core Mapping: Git ↔ Databricks Bundles


| Concept | Git | Databricks Bundle |
|---------|-----|-------------------|
| Development | Feature branch | Dev target |
| Release version | Git tag | Bundle version |
| Promotion | Redeploy same tag | Same bundle version |
| Environment config | N/A | Bundle targets |
| Rollback | Old tag | Redeploy old bundle version |


Databricks bundles are environment-aware, not version-aware by default — Git tags provide version immutability

---


### 2️⃣ Bundle Structure (Recommended)

```css
.
├── databricks.yml
├── resources/
│   ├── jobs.yml
│   ├── pipelines.yml
│   └── clusters.yml
├── src/
│   └── pipelines/
└── tests/
```

---

### 3️⃣ databricks.yml (Best Practice Template)

```yaml
bundle:
  name: research-pipeline
  version: ${BUNDLE_VERSION}

targets:
  dev:
    workspace:
      host: https://adb-xxxx.dev.azuredatabricks.net
    mode: development
    default: true

  uat:
    workspace:
      host: https://adb-xxxx.uat.azuredatabricks.net
    mode: production

  prod:
    workspace:
      host: https://adb-xxxx.prod.azuredatabricks.net
    mode: production
```

**Key Rules**
- bundle.version must come from Git tag
- Targets differ only in infra/config
- No code differences per environment

---

### 4️⃣ Parallel Feature Development → Dev

Git
```css
feature/A
feature/B
```

**Dev Deployment**

```bash
databricks bundle deploy \
  --target dev \
  --var BUNDLE_VERSION=feature-A-${GIT_SHA}
```

- ✔ Fast iteration
- ✔ Safe collisions avoided
- ✔ No tags involved

Feature deployments are ephemeral and not promoted

---

### 5️⃣ Integration → Release Version

After merging features into main:

```bash
git tag -a v2.3.0 -m "Release v2.3.0"
git push origin v2.3.0
```

CI extracts:
```bash
BUNDLE_VERSION=v2.3.0
```

---


### 6️⃣ Release Deployment (Critical Flow)


Deploy SAME tag to all environments

```bash
# Dev
databricks bundle deploy --target dev  --var BUNDLE_VERSION=v2.3.0

# UAT
databricks bundle deploy --target uat  --var BUNDLE_VERSION=v2.3.0

# Prod
databricks bundle deploy --target prod --var BUNDLE_VERSION=v2.3.0
```

- ✔ Same code
- ✔ Same bundle version
- ✔ Environment-specific infra only

---

### 7️⃣ Promotion Model (Important Clarification)

- 🚫 No environment branches
- 🚫 No re-build per env

Promotion is simply:

Redeploy(tag=v2.3.0, target=next-env)

---

### 8️⃣ Job & Pipeline Versioning (Recommended)


In resources/jobs.yml:

```yaml
resources:
  jobs:
    research_job:
      name: research-job-${bundle.version}
      tags:
        bundle_version: ${bundle.version}
        environment: ${bundle.target}
```

**Benefits**
- Job name shows version
- Metadata searchable
- Audit-friendly

---

### 9️⃣ Delta / Pipeline Audit (Highly Recommended)

Add bundle version to outputs:

```scala
df
  .withColumn("bundle_version", lit(sys.env("BUNDLE_VERSION")))
  .withColumn("deploy_env", lit(sys.env("BUNDLE_TARGET")))
```

- ✔ Lineage
- ✔ Debugging
- ✔ Rollback verification

---

### 🔟 Rollback in Databricks Bundles

**Scenario**

Prod issue in v2.3.0

**Action**
```bash
git checkout v2.2.5
databricks bundle deploy --target prod --var BUNDLE_VERSION=v2.2.5
```

- ✔ No branch
- ✔ No code change
- ✔ Immediate rollback

---

### 11️⃣ Hotfix Workflow (Databricks-Aligned)

```bash
git checkout -b hotfix/v2.3.1 v2.3.0

# fix bug
git commit
git tag -a v2.3.1
git push origin v2.3.1
```

**Deploy**:

```bash
databricks bundle deploy --target dev
databricks bundle deploy --target uat
databricks bundle deploy --target prod
```

---

### 12️⃣ CI/CD Reference Flow

```css
PR merged → main
↓
tag created (vX.Y.Z)
↓
CI builds once
↓
Deploy bundle vX.Y.Z → Dev
↓
Promote same bundle → UAT
↓
Promote same bundle → Prod
```

---

### 13️⃣ Anti-Patterns in Databricks Bundles (Avoid)


- ❌ Different code per target
- ❌ dev/uat/prod Git branches
- ❌ Retagging bundle versions
- ❌ Feature branches deployed to prod
- ❌ Rebuilding wheels per environment


Final Rule Set (Databricks-Specific)

1. Git tag = bundle version
2. Bundle version never changes
3. Targets change infra, not code
4. Promotion = redeploy same bundle
5. Rollback = redeploy old bundle

--