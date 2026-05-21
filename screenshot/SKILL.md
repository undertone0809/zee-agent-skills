---
name: "screenshot"
description: "Use for desktop or system screenshots when the user wants an app, window, region, or whole-desktop capture and no tool-specific capture fits. Prefer app/window capture over full-screen for desktop apps."
---

# Screenshot Capture

Follow these save-location rules every time:

1) If the user specifies a path, save there.
2) If the user asks for a screenshot without a path, save to the OS default screenshot location.
3) If Codex needs a screenshot for its own inspection, save to the temp directory.

## Decide the capture scope

Choose the narrowest capture that matches the task.

- Do not change focus, bring another app to the front, or otherwise interrupt the user's current work unless they explicitly ask for that behavior.
- If the user names an app, capture that app with `--app` first.
- If the user points at a dialog, settings pane, or titled window, add `--window-name` when possible.
- If the app has multiple candidate windows, run `--list-windows` first and then retry with `--window-id`.
- Use `--active-window` only when the user explicitly wants the current/frontmost window, or when the app is unknown but they can focus it.
- Use a full-screen capture only when the user explicitly wants the desktop, all monitors, or a composition spanning multiple apps.
- For Codex visual inspection of a desktop app, default to `--app "<App>" --mode temp`. Avoid `--active-window` if Codex, the terminal, or another unrelated app is frontmost.
- If a named macOS app is likely minimized and the user explicitly allows a brief focus change, retry with `--restore-minimized` so Codex can restore the app, capture it, then minimize it again and return focus.

This is the main guardrail for avoiding accidental screenshots of the user's working area.

## Tool priority

- Prefer tool-specific capture when available, such as Figma tooling for Figma files or Playwright/browser tools for browser and Electron surfaces.
- Use this skill for desktop apps, OS-level captures, and cases where a tool-specific capture path cannot get the right image.

## Use the bundled helpers

Default to the bundled scripts instead of re-deriving native OS commands.

On macOS, run the permission preflight before window or app capture:

```bash
bash <path-to-skill>/scripts/ensure_macos_permissions.sh
```

The helpers route Swift's module cache to `$TMPDIR/codex-swift-module-cache` to avoid extra module-cache prompts.

Primary helper:

```bash
python3 <path-to-skill>/scripts/take_screenshot.py
```

## Common commands

- Named app capture for inspection on macOS:

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --app "Figma" --mode temp
```

- Briefly restore a minimized macOS app, capture it, then minimize it again:

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --app "Rudder" --restore-minimized --mode temp
```

- Specific window title inside an app on macOS:

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --app "Codex" --window-name "Settings" --mode temp
```

- Disambiguate multiple windows on macOS:

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --list-windows --app "Codex"
python3 <path-to-skill>/scripts/take_screenshot.py --window-id 12345 --mode temp
```

- Explicit frontmost-window capture:

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --active-window --mode temp
```

- Explicit region crop:

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --mode temp --region 100,200,800,600
```

- Explicit output path:

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --path output/screen.png
```

- Default full-screen capture when the user explicitly wants the desktop:

```bash
python3 <path-to-skill>/scripts/take_screenshot.py
```

The script prints one saved path per capture. When multiple windows or displays match, it prints multiple paths, usually with suffixes like `-w<windowId>` or `-d<display>`.

## Platform notes

- `--app`, `--window-name`, and `--list-windows` are macOS-only.
- On Linux, use `--active-window`, `--window-id`, or `--region` when you need something narrower than full screen.
- On Windows, use `scripts/take_screenshot.ps1`; prefer `-ActiveWindow`, `-Region`, or `-Path` the same way you would use the Python helper flags.
- On macOS, full-screen capture may produce one file per display. On Linux and Windows, full-screen capture usually uses the virtual desktop.
- On Linux, the helper prefers `scrot`, then `gnome-screenshot`, then ImageMagick `import`.

## Fast workflows

- "Take a look at <App> and tell me what you see": use `--app "<App>" --mode temp`. Do not start with a full-screen capture, and do not steal focus from whatever the user is doing now.
- "The app is running but probably minimized; take a look anyway": use `--app "<App>" --restore-minimized --mode temp`, but only if the user explicitly allows that brief restore/minimize cycle.
- "I only need one panel from an app with multiple windows": use `--list-windows`, then `--window-id`.
- "Grab whatever is frontmost": use `--active-window`.
- "Compare implementation against Figma": capture the Figma design with Figma tooling first, then capture the running app with this skill.

## Error handling

- On macOS, run `bash <path-to-skill>/scripts/ensure_macos_permissions.sh` first to request Screen Recording in one place.
- If macOS app/window capture returns no matches, run `--list-windows --app "AppName"` and retry with `--window-id`, and make sure the app is visible on screen.
- If macOS app capture returns no matches because the app is minimized and the user allows focus changes, retry with `--app "AppName" --restore-minimized`. This path intentionally steals focus for a moment, captures the restored window, then minimizes it again and re-activates the previously frontmost app.
- If the frontmost window is Codex, the terminal, or another unrelated app, do not use `--active-window`; switch to `--app "<TargetApp>"` instead.
- If the target app is hidden or off-screen, ask the user to make it visible rather than activating it yourself unless they explicitly asked you to bring it forward.
- If Linux region/window capture fails, check tool availability with `command -v scrot`, `command -v gnome-screenshot`, and `command -v import`.
- If native helpers fail and you must fall back, use the platform screenshot tool that best matches the requested scope, such as `screencapture`, `scrot`, `gnome-screenshot`, `import`, or the bundled Windows PowerShell helper.
- Always report the saved file path in the response.
