# Online Activity 3: Application Servers Recap

*COMP 1350 — Web Administration — distributed Week 2, due before Week 3*

## Why This Matters

So far Apache and Nginx have only served static files. Week 3 introduces the idea of an application server — something that runs your actual code — and Node.js/Express specifically. This activity gets the core distinction into your head before lecture.

## Before Class: Read

- [MDN — Node.js server without a framework](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Express_Nodejs/Introduction) — the "Introduction to Express" MDN page; just the first two sections
- [nodejs.org — About Node.js](https://nodejs.org/en/about) — one page, explains what Node actually is and why it's non-blocking

## Come to Class Ready to Answer

1. In one sentence: what's the difference between a *web server* and an *application server*?
2. Node.js is described as "non-blocking" and "event-driven." Where have you heard one of those words before this term (hint: Week 2)?
3. If you run `node server.js` in a terminal and then close that terminal, what happens to your running app? Why is that a problem in production?
4. Name a language/framework other than Node.js/Express that could also serve as an "application server" (the reading mentions a few common ones, or think of what you already know).

## How This Feeds Forward

- These questions form part of **Quiz 3**, given in Week 3.
- Week 3's lecture builds your first real Express app and introduces PM2 — the tool that directly answers question 3 above.
