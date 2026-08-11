---
title: "Lab 7: OAuth Login with Passport.js"
---

[&larr; Back to course index]({{ '/' | relative_url }})

{% raw %}
# Lab 7: OAuth Login with Passport.js

*COMP 1350 — Web Administration, Week 7*

In this lab you'll add "Sign in with Google" to your Node/Express app using Passport.js — implementing the OAuth flow covered in this week's lecture end to end, on your own running application.

> **Apple Silicon (M1/M2/M3/M4) Mac?** See Lab 1's Apple Silicon Setup section first. Replace `ubuntu/jammy64` below with your arm64 box, add a `vmware_desktop` provider block instead of the VirtualBox one, and run `vagrant up --provider=vmware_desktop`. Everything else in this lab — IPs, commands, config files — is identical.

## Part 1: Provision the VM

```bash
mkdir ~/comp1350-lab7 && cd ~/comp1350-lab7
vagrant init ubuntu/jammy64
```

Add to the `Vagrantfile`:

```ruby
config.vm.network "private_network", ip: "192.168.56.17"
```

```bash
vagrant up
vagrant ssh
sudo apt update
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

1. On your **host machine**, map a domain name to this VM so Google's OAuth redirect works cleanly (OAuth providers are picky about `localhost`/raw IPs for redirect URIs):

```
192.168.56.17 wsa-lab7.local
```

## Part 2: Scaffold the Express App

```bash
sudo npm install -g express-generator
express lab7-oauth
cd lab7-oauth
npm install
```

1. Start it and confirm the default page loads at `http://wsa-lab7.local:3000` from your host browser:

```bash
npm start
```

2. Stop the server (Ctrl+C). Install `ejs` as the view engine and switch the default view files over:

```bash
npm install ejs
mv views/index.jade views/index.ejs
mv views/error.jade views/error.ejs
```

3. Replace `views/index.ejs` with:

```html
<html>
  <body>
    <%= title %>
  </body>
</html>
```

## Part 3: Register OAuth Credentials with Google

1. Go to [console.developers.google.com](https://console.developers.google.com/project) and create a new project named `wsa-lab7`.
2. From the sidebar, go to **APIs & Services → OAuth consent screen**. Choose **External**, fill in the app name and your email for support/developer contact, and accept defaults for the remaining screens.
3. Go to **Credentials → Create Credentials → OAuth client ID**. Choose **Web application** and fill in:
   - **Name**: `wsa-lab7`
   - **Authorized JavaScript origins**: `http://wsa-lab7.local`
   - **Authorized redirect URIs**: `http://wsa-lab7.local:3000/auth/google/callback`
4. Click **Create**. Copy the **Client ID** and **Client Secret** shown in the popup — you'll need both in Part 4.

**Never commit these values to Git.** In Part 4 you'll load them from environment variables, exactly like the PaaS environment-variable practice from Week 4.

## Part 4: Install Passport and the Google Strategy

1. Install the required packages:

```bash
npm install passport express-session passport-google-oauth20 --save
```

2. Set your credentials as environment variables (don't hardcode them):

```bash
export GOOGLE_CLIENT_ID="your-client-id-here"
export GOOGLE_CLIENT_SECRET="your-client-secret-here"
```

3. Near the top of `app.js`, add:

```js
var passport = require('passport');
var session = require('express-session');
var GoogleStrategy = require('passport-google-oauth20').Strategy;

passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: 'http://wsa-lab7.local:3000/auth/google/callback'
  },
  function(accessToken, refreshToken, profile, cb) {
    cb(null, profile);
  }
));
```

4. Right after the Express app is created, add:

```js
app.use(session({ secret: 'comp1350-lab7-secret' }));
app.use(passport.initialize());
app.use(passport.session());

passport.serializeUser(function(user, done) { done(null, user); });
passport.deserializeUser(function(user, done) { done(null, user); });
```

## Part 5: Add the Auth Routes

1. Near the other route imports in `app.js`:

```js
var auth = require('./routes/auth');
```

2. Alongside the other `app.use('/...')` lines:

```js
app.use('/auth', auth);
```

3. Create `routes/auth.js`:

```js
var express = require('express');
var passport = require('passport');
var router = express.Router();

router.route('/google').get(
  passport.authenticate('google', {
    scope: ['profile', 'email']
  })
);

router.route('/google/callback').get(
  passport.authenticate('google', { failureRedirect: '/' }),
  function(req, res) {
    res.redirect('/');
  }
);

module.exports = router;
```

4. Create `views/users.ejs`:

```html
<html>
  <body>
    <div>Hi <%= username %></div>
  </body>
</html>
```

5. Replace `routes/index.js`:

```js
var express = require('express');
var router = express.Router();

router.get('/', function(req, res) {
  if (req.user && req.user.displayName) {
    res.render('users', { username: req.user.displayName });
  } else {
    res.render('index', { title: 'wsa-lab7' });
  }
});

module.exports = router;
```

6. Update `views/index.ejs` to add a login link:

```html
<html>
  <body>
    <%= title %>
    <ul>
      <li><a href="/auth/google">Sign in with Google</a></li>
    </ul>
  </body>
</html>
```

## Part 6: Test the Full Flow

1. Restart the app with your environment variables set:

```bash
GOOGLE_CLIENT_ID="..." GOOGLE_CLIENT_SECRET="..." npm start
```

2. From your host browser, visit `http://wsa-lab7.local:3000` and click **Sign in with Google**.
3. Complete the Google login/consent screen. You should be redirected back and see "Hi `<your name>`".

**Q1**: At what point in this flow did your app ever see your Google password? Trace through exactly which party (browser, your app, Google) held which piece of information at each step.

## Deliverables

- Screenshot of the login page with the "Sign in with Google" link
- Screenshot of the post-login "Hi `<your name>`" page
- Your `app.js` OAuth configuration section (with credentials redacted/shown as environment variable references, never as literal strings)
- Your written answer to Q1
{% endraw %}
