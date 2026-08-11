# Online Activity 7: Authentication Concepts Recap

*COMP 1350 — Web Administration — distributed Week 6, due before Week 7*

## Why This Matters

This is the last content week before the midterm. Week 7 covers authentication broadly before landing on OAuth specifically. This activity gets the foundational vocabulary — and one very common point of confusion — sorted out before class.

## Before Class: Read

- [OWASP — Authentication Cheat Sheet (intro section only)](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) — read just the overview, not the full technical cheat sheet
- [Auth0 / Okta — What is OAuth 2.0?](https://auth0.com/intro-to-iam/what-is-oauth-2) — a widely used, clear explainer on OAuth from an identity vendor
- [OAuth.net — OAuth 2.0 (homepage)](https://oauth.net/2/) — skim the top of the page for the official framing

## Come to Class Ready to Answer

1. What is the difference between authentication and authorization? Give an example where you could be authenticated but not authorized to do something.
2. Passwords should never be stored in plaintext or "merely encrypted." What's the actual difference between encryption and hashing in this context, and why does it matter for password storage?
3. Based on the OAuth reading, what problem is OAuth actually solving? What would the alternative (without OAuth) look like when you click "Sign in with Google" on a third-party app?
4. Name the four roles in an OAuth flow, in your own words (the reading names them, though possibly with different exact terms).

## How This Feeds Forward

- These questions form part of **Quiz 7**, given in Week 7 — the last quiz before the midterm.
- Week 7's lecture and lab have you implement real "Sign in with Google" login using Passport.js on your own Express app.
