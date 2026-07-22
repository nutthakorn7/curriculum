<!-- Sandbox/teaching only; for authorized lab use. -->

# Dependency Confusion / Typosquat — Controlled Walkthrough

**OWASP 2025:** A03 Software Supply Chain Failures
**CWE:** CWE-1357 (reliance on insufficiently trustworthy component),
CWE-829 (inclusion of functionality from untrusted control sphere)

> This scenario is run only against the instructor-provided private registry
> in an isolated lab network. Never plant packages on the real PyPI/npm.

---

## The two attacks

### 1. Typosquatting
The attacker publishes a package whose name is a near-miss of a popular one
and waits for a fat-fingered `pip install`.

| Legit | Typosquat |
|-------|-----------|
| `requests` | `reqeusts`, `request` |
| `urllib3`  | `urlib3` |
| `python-dateutil` | `python-dateutil3` |

A single typo pulls attacker code that runs at install time
(`setup.py` / build scripts execute as you).

### 2. Dependency confusion (substitution)
A company uses an **internal** package, e.g. `acme-internal-utils`, that
exists only on its private registry. The attacker publishes a package with the
**same name** but a **higher version number** on the *public* registry. If the
build resolver checks both registries and simply prefers the highest version,
it pulls the attacker's public package instead of the internal one.

```
private registry:  acme-internal-utils == 1.4.0   (the real one)
public  registry:  acme-internal-utils == 99.0.0  (the attacker's)
resolver picks: ----------------------> 99.0.0     # confusion!
```

---

## Lab steps (controlled)

1. **Observe the pull.** Configure pip to see both the lab's private index and
   the lab's "public" index. Install `acme-internal-utils` and note which
   version/registry it came from (`pip install -v` prints the source URL).
2. **Trigger confusion.** The instructor's "public" index already hosts a
   higher-versioned look-alike. Re-resolve and watch the wrong one win.
3. **Inspect the payload.** The look-alike's `setup.py` only writes a
   `PWNED.txt` marker (benign) — proof that install-time code ran.

---

## Defenses (apply, then re-run step 2 — confusion should stop)

- **Pin + lockfile with hashes.** `pip install --require-hashes -r requirements.txt`
  (or a committed lockfile). A hash mismatch blocks substitution.
- **Scope / namespace internal packages.** Reserve the public name, or use a
  private namespace so a public package can never collide.
- **Single trusted index.** Don't merge public + private indexes; use
  `--index-url` (one source) not `--extra-index-url` (resolver shops around).
- **Allow-list / proxy registry.** Pull everything through one curated mirror
  (e.g. Artifactory/Nexus) that you control.
- **SCA in CI.** Flag newly-introduced or suspiciously-versioned packages
  (tie back to `sca_scan.sh`).

## Deliverable
A short note: which registry served the package before vs. after your fix,
plus the one defense you found most effective and why.
