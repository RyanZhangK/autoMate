# autoMate Bridge — browser extension

Gives the local autoMate hub control of **your** browser — your tabs, your
logged-in sessions, your cookies. Without this extension, autoMate's
`browser.*` tools spawn an empty Chromium via Playwright and have to log
in from scratch every time.

## Install (Chrome / Edge / Brave / any Chromium ≥ 116)

1. Make sure `automate serve` is running.
2. Open `chrome://extensions`, toggle **Developer mode** on (top-right).
3. Click **Load unpacked**, select this folder.
4. The toolbar icon should flip to a green **ON** badge within a couple of
   seconds. Click the icon to confirm `Connected to autoMate`.

That's it. autoMate's chat will now be able to call `bx.tabs`, `bx.click`,
`bx.extract`, etc. against your live browser.

## Tools it exposes

| autoMate tool       | what it does                                      |
| ------------------- | ------------------------------------------------- |
| `bx.tabs`           | list open tabs                                    |
| `bx.open`           | open a new tab at a URL                           |
| `bx.activate`       | switch focus to a tab                             |
| `bx.close`          | close a tab                                       |
| `bx.navigate`       | navigate the active tab to a URL                  |
| `bx.screenshot`     | capture the visible area of the active tab        |
| `bx.click`          | click an element (CSS or `text=...` selector)     |
| `bx.type`           | type into an input (optionally submit)            |
| `bx.extract`        | pull text / html / links / page meta              |
| `bx.scroll`         | scroll up/down/top/bottom                         |
| `bx.eval`           | evaluate a JS expression in-page (high power)     |

## Talking to a non-default server

If you ran the server on a custom host/port, click the extension icon, paste
the WebSocket URL (e.g. `ws://192.168.1.20:8765/api/extension/ws`), and hit
Save & reconnect.

## Privacy

The extension talks to `127.0.0.1` by default. No data leaves your machine.
The autoMate server only accepts one extension connection at a time.

## Firefox

Firefox MV3 is broadly compatible — `chrome.*` APIs are aliased — but support
varies. PRs welcome.
