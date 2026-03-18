# Heroku Deployment Guide

## Prerequisites
- Heroku CLI installed (`brew tap heroku/brew && brew install heroku`)
- Logged in (`heroku login`)
- A TBA API key from https://www.thebluealliance.com/account

## 1. Create the Heroku App

```bash
heroku create scoutpro-9771
```

## 2. Add PostgreSQL

```bash
heroku addons:create heroku-postgresql:essential-0
```

This automatically sets `DATABASE_URL`.

## 3. Set Environment Variables

```bash
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set TBA_API_KEY=your_tba_key_here
heroku config:set FLASK_ENV=production
```

## 4. Deploy

```bash
git push heroku main
```

## 5. Run Migrations & Seed

```bash
heroku run flask db upgrade
heroku run flask seed
```

To import match schedules for each event:
```bash
heroku run flask import-matches 2025mitraverse
heroku run flask import-matches 2025mibig
```

## 6. Verify

```bash
heroku open
```

You should see the login page. Create a user, select an event, and confirm the home screen loads.

## Useful Commands

```bash
# View logs
heroku logs --tail

# Open a shell
heroku run bash

# Run seed with demo scouting data
heroku run flask seed-demo

# Check database
heroku pg:info

# Restart
heroku restart
```

## Updating

After pushing new code:
```bash
git push heroku main
heroku run flask db upgrade   # only if migrations changed
```
