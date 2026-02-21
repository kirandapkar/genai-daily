# Daily build script

Runs at **00:00 IST** (midnight) to sync/push the repo. Requires Mac system timezone set to **India Standard Time** for correct schedule.

## Install (run daily at 00:00 IST)

```bash
cp /Users/kirandapkar/Documents/projects/genai-daily/scripts/com.genaidaily.dailybuild.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.genaidaily.dailybuild.plist
```

## Uninstall

```bash
launchctl unload ~/Library/LaunchAgents/com.genaidaily.dailybuild.plist
```

## Manual run

```bash
cd /Users/kirandapkar/Documents/projects/genai-daily
./scripts/daily-build-and-push.sh          # push any uncommitted changes
./scripts/daily-build-and-push.sh --dummy  # test: create dummy, test, push
./scripts/daily-build-and-push.sh --delete-dummy  # remove dummy after test
```

Logs: `scripts/daily-build.log`, `scripts/daily-build.err`

## Env

Script loads `GITHUB_TOKEN` from `../.cursor/rules/.env` (or set `ENV_FILE`).
