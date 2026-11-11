{% if course_code == '02005094' %}# Week 5 — XSS and browser request controls

**OWASP 2025:** A05 Injection / CWE-79 (XSS); A01 Broken Access Control / CWE-352 (CSRF). [Worksheet 5](worksheet.md) is the student contract.

## Class flow

10-minute quiz/review + 15-minute mechanism demo + 100-minute common practical + 20-minute debrief + 5-minute evidence exit. The quiz covers contextual output encoding, CSP and SameSite. The practical is worth 60 points; each student completes only their assigned Conventional or AIR-Sec format for the remaining 40. Follow-up writing is outside the 100-minute core. The minute budgets have not been validated with a representative student.

## Prepare once, then run offline

```bash
cd labs/week05-xss-client-side
docker compose build
docker compose up --no-build --pull never
```

The image pins Flask 3.1.3. No runtime `pip install` or network access is needed after the image has been built. Open `http://localhost:8080/` before testing `/comments`. The service binds only to `127.0.0.1`. To host the supplied attack page on a different origin, start `python3 -m http.server 8081 --bind 127.0.0.1` from this directory and visit `http://localhost:8081/csrf.html`.

Two localhost ports are different **origins** but the same **site**. The vulnerable endpoint requires the session cookie but accepts a comment without a CSRF token. The reference `fixed_app.py` checks a server-generated token and escapes output. Students first fix the provided `student_patch.py` and run `student_checks.py`, then test `student_app.py` in the browser. See the worksheet for the exact commands and required normal/attack controls.

The sandbox session value is deliberately fixed. The reference is a teaching example, not a production authentication pattern; production needs per-user random sessions, HTTPS and a Secure cookie.

## References

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP Top 10:2025 A01](https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/) and [A05](https://top10.owasp.org/2025/A05_2025-Injection/)
{% else %}# {{ slot_label }} — Cross-Site Scripting (XSS) & Client-Side Risks

**OWASP 2025:** A05 Injection / CWE-79 (XSS); A01 Broken Access Control / CWE-352 (CSRF)

## ✅ This week — what to do
1. **Before class** — Docker Desktop working ({{ ref('threat-modeling') }} *Lab 0*); skim last week's recap.
2. **Slides, then class** — read `{{ slides }}` and answer the worksheet's **Part 2** before class; class opens with the weekly quiz (~10 min) and a short explanation + demo (~15 min).
3. **Lab (in class)** — play this week's game, then complete **Worksheet 5** (`worksheet.md`, Parts 1–4, incl. *Audit the AI* + *EiPE/Prompt*). Kickoff: `docker compose build` once online, then `docker compose up --no-build --pull never` → http://localhost:8080. Part 3 marks each task *in class* or *homework*.
4. **Submit before the next class** (homework tasks included) — worksheet PDF → `learn.zcr.ai/submit` · code → GitHub · weekly quiz → `learn.zcr.ai/quiz`. (How: [SUBMISSION.md](../../SUBMISSION.md).)
5. **Project** — apply this week's lesson to your [NoteVault project](../../project/README.md) where it fits.

*Time breakdown: [AGENDA.md](../../AGENDA.md). Grading: see the worksheet rubric.*

## Objectives
- Distinguish reflected, stored, and DOM-based XSS.
- Understand the same-origin policy, cookies (SameSite), and CSP.
- Build a CSRF PoC and defend against it.

## ⛳ Signature game — "XSS Golf" (this lab's own app)
1. Land a **reflected** and a **stored** XSS payload. (DOM XSS needs a separate target — Juice Shop — and is optional; our app doesn't expose one.)
2. Steal/abuse a session via the XSS (sandbox only; HttpOnly is missing, so JS can read the cookie).
3. Build a CSRF page that performs a state-changing request.
4. **Fix:** add contextual output encoding, a strict Content-Security-Policy, and hardened cookies (`HttpOnly`/`SameSite`; use `Secure` on HTTPS) — verify the **XSS** now fails. The vulnerable endpoint requires the sandbox session cookie but no CSRF token. The reference `fixed_app.py` checks both and rejects the forged POST with 403.

## Run the local target
```bash
docker compose build     # once while online
docker compose up --no-build --pull never  # vulnerable_app.py on http://localhost:8080
```
The fixed version is `fixed_app.py`.

## Deliverable
Working payloads + CSP/encoding/CSRF fixes + screenshots of blocked attacks.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
{% endif %}