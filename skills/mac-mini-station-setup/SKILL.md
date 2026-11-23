---
name: mac-mini-station-setup
description: Walks the user through turning a Mac mini into an always-on AI station, one step at a time, and verifies what it can with read-only Mac terminal commands. Covers never-sleep settings, automatic login and FileVault, the Claude desktop app with Remote Control, Chrome Remote Desktop, moving the working folder onto the Mac, and a one-press screenshot-to-clipboard shortcut. Use when the user says "walk me through the Mac mini setup", "set up my Mac mini", "check my always-on settings", "is my Mac set to never sleep", "set up Chrome Remote Desktop", or "set up the screenshot shortcut".
---

# Mac mini station setup

You are guiding a smart non-developer through setting up a Mac mini as an always-on AI station. The companion document is `GUIDE.md` in this skill folder (Sections A to F). If it is in the working folder, read it first and keep your instructions consistent with it.

## Ground rules (read before doing anything)

1. **One step at a time.** Give one instruction, wait for the user to say done (or paste a screenshot), verify if you can, then move on. Never dump the whole checklist.
2. **Plain language.** Say exactly what to click. Explain a term the first time you use it.
3. **The terminal is for read-only checks, always.** The commands in the "Check" blocks below only read settings. Run them and explain the result in one or two plain sentences. Do not paste raw output at the user unless they ask. Do not use the terminal to change settings, install software, start or stop services, or run downloaded code, even after the user approves a change. Approved changes are made by the user in System Settings or the relevant app.
4. **Ask before every system-setting change.** A request to "walk me through setup" is not approval for each change. Before each one (power settings, login items, keyboard shortcuts, installing an app), say what the change is and what it affects, ask whether the user wants it, and wait for a clear yes. Then tell them where to click.
5. **Never change security settings yourself, through any tool, even when asked.** This includes: FileVault, automatic login, passwords, the firewall, Gatekeeper, System Integrity Protection, anything under Privacy & Security (Accessibility, Screen Recording, Input Monitoring, Full Disk Access), sharing services, Remote Login, and the Chrome Remote Desktop PIN. Explain the trade-off, let the user decide, and let the user click it. Never suggest bypassing a security warning.
6. **Never run `sudo`. Never ask for or handle the user's Mac password, Google password, PIN, recovery key or sign-in codes.** If a step needs one, the user types it into the macOS or app dialog, not into this chat. If a command would need `sudo` to work, stop and have the user check the matching screen in System Settings instead.
7. **Do not invent menu names.** macOS labels shift between versions. If you are unsure of an exact label, say "look for something like ..." and suggest the search box at the top of System Settings.
8. **Keep a progress note, with permission.** At the start, ask: "May I keep a small progress note named mac-mini-setup-progress.md in this folder as we go? It holds setup status and your decisions, never passwords." If yes, update it after each section using your file-editing tool (not the terminal) with what is done, what was skipped, and any decision the user made (for example "kept FileVault on"). If the user comes back later, read it and resume. If no, keep the checklist in the chat.
9. **Screenshots are welcome, with care.** When you ask for a screenshot, remind the user once to check it for private messages, account details or login codes first.

## Start

Run these, then tell the user in one line what Mac and macOS version they have.

```bash
sw_vers
sysctl -n hw.model
```

If this is not a Mac (the commands fail), stop and say this skill must be run on the Mac mini itself.

Ask: "Do you want to go through everything from the top, or jump to one section (A always-on, B Claude app and Remote Control, C Chrome Remote Desktop, D your working folder, E screenshot shortcut)?"

## Section A: Always on

### A1. Sleep settings

Check:

```bash
pmset -g
pmset -g custom
```

How to read it (`pmset -g custom` shows the saved wall-power profile, `pmset -g` shows what is active now):
- `sleep` should be `0`. That turns off the idle sleep timer. Any other number is minutes until sleep. It does not prevent someone choosing Sleep by hand, a shutdown or a restart.
- `displaysleep` can be any number. It is the display timer in minutes, and the display turning off is fine.
- `disksleep` is about spinning drives. `0` is tidy but it is not required on a Mac mini's internal storage.
- `womp` `1` means "Wake for network access" is on. It helps, but it is not a promise that a sleeping Mac can be woken from the internet.
- `autorestart` `1` means the Mac starts back up after a power failure.
- If a key is missing from the output, say "not reported on this Mac" and check the Energy screen with the user. Do not guess a value.

For anything that needs changing, explain it, ask whether the user wants the change, and if yes have them make it in **System Settings > Energy**:
- "Prevent automatic sleeping when the display is off": on
- "Wake for network access": on
- The power-recovery control: either a switch named "Start up automatically after a power failure" (on), or a menu named "Start up when power is connected" (choose "After power failure"). Which one appears depends on the Mac model and macOS version.
- "Put hard disks to sleep when possible": off, if shown (optional)

Then run `pmset -g` again and confirm. These values can also be set with `pmset` in the terminal, but that is a change and needs `sudo`, so never do it. The user clicks.

To see whether something is currently keeping the Mac awake or trying to sleep it:

```bash
pmset -g assertions
```

### A2. Display

Tell the user: in System Settings > Lock Screen, the display-off timer (look for "Turn display off when inactive", possibly with "on power adapter" in the label) can be any value they like. A screen saver or a locked screen does not mean the computer is asleep. Do not suggest weakening the password requirement on that page. Nothing to verify beyond `displaysleep` above.

### A3. Automatic login and FileVault (security: user decides, user clicks)

Check:

```bash
fdesetup status
defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser
```

How to read it:
- `fdesetup status` reports whether FileVault is on. It changes nothing. If it cannot report, do not retry with `sudo`. Ask the user to look at System Settings > Privacy & Security > FileVault.
- The second command prints an account name if automatic login has been set. An error saying the key does not exist usually means automatic login is off, but treat it as a clue, not proof. Confirm by having the user look at System Settings > Users & Groups > "Automatically log in as".

Explain the trade-off in plain words:
- FileVault on (recommended): macOS does not allow automatic login. After a cold start or power failure, plan for someone to type the password at the Mac itself. Chrome Remote Desktop cannot reach the Mac until that first unlock. A locked screen on an already running Mac is different: remote access usually still connects and the user can unlock it there.
- FileVault off plus automatic login: the Mac comes back by itself after a restart. The cost: the user gives up the protection FileVault adds on top of the Mac's built-in storage encryption, and anyone with physical access can start the Mac straight into the user's account without a password.

Ask which they want. Do not recommend turning FileVault off. If they choose automatic login, tell them where to click (System Settings > Privacy & Security > FileVault, then System Settings > Users & Groups > "Automatically log in as") and let them do it. If "Automatically log in as" is dimmed, the usual cause is FileVault, but a managed Mac or an Apple Account based login password can also block it. Do not change anything to force it. Record their choice in the progress note.

If the user asks about unlocking remotely after a restart: macOS Tahoe 26 on Apple silicon supports FileVault unlock over SSH when Remote Login was set up beforehand. That is an advanced, separate security decision. Do not set it up as part of this walkthrough.

### A4. Power and network

Check whether the Mac is on a wired connection:

```bash
route -n get default 2>/dev/null | grep interface
networksetup -listallhardwareports
```

Match the default interface (for example `en0`) to its hardware port name. If it is Wi-Fi, mention that ethernet is steadier if a cable is practical. It is a suggestion, not a requirement.

Remind them: plugged into an outlet nobody switches off.

### A5. The Sleep menu

There is nothing to verify. Tell the user that nobody should click Apple menu > Sleep or press the power button on this Mac, and suggest a sticky note. If it is put to sleep by hand, remote access may stop, and network wake is not a dependable way back.

### A6. Idle test

Save this for after Sections B and C. Have the user leave the Mac untouched for longer than the display timer, then connect from the laptop and send a message before touching the Mac. Do not suggest unplugging power as a test.

## Section B: Claude desktop app and Remote Control

Check the app is installed:

```bash
ls /Applications | grep -i claude || echo "Claude app not found in Applications"
```

If the user is talking to you in a local Code session in the Claude desktop app on the Mac mini itself, the install is confirmed. Say so. A regular chat, a cloud session, or a session running on another computer does not confirm it, so check that `sysctl -n hw.model` reports a Mac mini.

Then guide, one step at a time:
1. The working folder: confirm this session is opened on their ai-workspace folder (`pwd`). If the folder is not on the Mac yet, do Section D and come back.
2. Remote Control: have them turn on the Remote Control switch for this session, or type `/remote-control` in the message box. To cover future sessions, in the app's Settings look for the Code section (called Claude Code in some versions) and an option like "Connect new sessions to Remote Control". Labels vary by version, so describe these as "look for". You cannot verify this from the terminal. Ask them to confirm by opening claude.ai/code on their laptop (same Claude account), finding this exact session and sending a message.
3. "Keep computer awake while Claude works": same Settings area, if their version shows it. Ask them to confirm it is on. Section A remains the main protection.
4. Phone: Claude mobile app, same account, Code section.
5. Optional, and ask first because it is a login item: right-click the Claude icon in the Dock > Options > Open at Login. Explain that this only launches the app after login. It does not resume unfinished work, so after any restart they should check that the session is connected and scheduled tasks are still on.

## Section C: Chrome Remote Desktop

Check Chrome and the host:

```bash
ls /Applications | grep -i "Google Chrome" || echo "Chrome not found"
ls /Library/PrivilegedHelperTools 2>/dev/null | grep -i -E "chrome|remot" || echo "Chrome Remote Desktop host not found in the usual place"
pgrep -fl -i "remoting|ChromeRemoteDesktop" || echo "No Chrome Remote Desktop process seen"
```

These checks are best effort. File and process names can differ between versions, so if they come back empty but the user says it works, believe the working connection.

Guide, one step at a time:
1. In Chrome on the Mac mini: sign in to Google, go to `remotedesktop.google.com/access`, use "Set up remote access", download and run the installer.
2. Name the computer and choose a PIN of at least 6 digits. Tell them not to tell you the PIN and not to reuse one from elsewhere.
3. Permissions (security: the user clicks these, you never do). Have them follow the prompts Chrome Remote Desktop shows during setup. In System Settings > Privacy & Security:
   - Accessibility: on for the Chrome Remote Desktop host, usually listed as ChromeRemoteDesktopHost. This allows mouse and keyboard control.
   - Screen & System Audio Recording (may be labeled Screen Recording): on for the Chrome Remote Desktop host. Here it may be listed as ChromeRemoteDesktopHost or under a technical name such as `org.chromium.chromoting.me2me.sh`. This allows viewing the screen.
   - Input Monitoring: only if the setup specifically asks for it.
   Tell them to match the entry to what the installer asked for and not to approve an unrelated app with a similar name. You cannot read these permissions from the terminal. Ask the user to confirm each one by looking, or to paste a screenshot.
4. From the laptop: Chrome > `remotedesktop.google.com/access` > same Google account > click the Mac mini > PIN.
5. Comfort tips: the arrow tab on the right edge opens session options. Mention full-screen, scale or resize to fit, clipboard sync (dependable for text, not for images), and "Configure key mappings" for Windows laptops. On a Windows keyboard the Windows key usually acts as Command, so have them test copy and paste first and map a spare key only if needed. Describe these as "look for", since the panel changes over time.
6. If they plan to unplug the monitor, mention that a headless Mac can give a small remote screen. Try the scale and resize options first. If needed, keep a display connected or consider an HDMI dummy plug. Results vary by Mac.

## Section D: Working folder

Goal: one local "home" copy at `~/ai-workspace` (or the name they prefer), not inside a cloud-synced location.

Check:

```bash
ls -d ~/ai-workspace 2>/dev/null && du -sh ~/ai-workspace || echo "No ~/ai-workspace folder yet"
pwd
```

If the current working folder path contains `Mobile Documents`, `CloudStorage`, `Google Drive`, `Dropbox`, or `OneDrive`, explain that working live inside a synced folder can cause missing or duplicated files, and suggest moving the working copy to the home folder.

Before any upload or copy, have the user do a privacy check: passwords, API keys, login tokens, `.env` files, and client or financial information they should not put in a cloud account stay out of the upload. If the folder holds that kind of material, suggest AirDrop or a USB drive, which do not go through a cloud service.

Guide the move (recommended: upload to Google Drive from the laptop, download on the Mac mini, unzip, drag into the home folder). Alternatives: Google Drive for desktop, AirDrop, USB drive. The user does the moving in Finder. Do not move, delete or overwrite the user's folders yourself, and never delete the original copy. Let the user confirm the new copy is complete before treating it as the main one.

After the copy, spot check with the user: list the top-level folders and ask if it looks right.

```bash
ls ~/ai-workspace | head -n 40
```

Backup: mention the options (a private GitHub repository, a weekly zip to Google Drive, or Time Machine) and let the user pick. Setting up a backup is outside this walkthrough's read-only boundary, so if they want git, treat it as a separate task they ask for after setup is finished. For that later task: the repository must be private, scan for secrets (passwords, API keys, `.env` files) and private client files before the first push, and ask before creating anything. Note that running `git` on a fresh Mac can pop up an offer to install Apple's developer tools. That is an install, so it is the user's decision.

## Section E: Screenshot to clipboard shortcut

Target: "Copy picture of screen to the clipboard" on one easy shortcut, so the user can press it and then paste into Claude with Cmd+V.

Check the current setting (read-only):

```bash
defaults read com.apple.symbolichotkeys AppleSymbolicHotKeys
```

How to read it. Find entry `29`, which is "Copy picture of screen to the clipboard" (28 is save screen to file, 30 is save selected area to file, 31 is copy selected area to clipboard). Inside it:
- `enabled = 1` means the shortcut is on.
- `parameters` holds three numbers: the character code, the key code, and the modifier total.
- Modifier total is a sum of: Shift 131072, Control 262144, Option 524288, Command 1048576. So Control alone is 262144, Control+Option is 786432, and the default Control+Shift+Command is 1441792.
- Key code 3 is F, 5 is G, 9 is V, 20 is the number 3 (US keyboard layout).
- Examples: the default looks like (51, 20, 1441792). Control+F looks like (102, 3, 262144). The first number can differ by keyboard layout or show as 65535, so rely on the second and third.

This is a clue, not the final word. These numbers are an internal macOS detail that Apple does not document. If entry 29 is missing or the command fails, say "I could not confirm it from here" and have the user look at System Settings > Keyboard > Keyboard Shortcuts > Screenshots. A missing entry does not prove the default is active. If the numbers do not decode cleanly, do not guess. Ask the user to read you what System Settings shows.

Guide the change (user clicks):
1. System Settings > Keyboard > "Keyboard Shortcuts..." button > Screenshots.
2. Make sure "Copy picture of screen to the clipboard" is ticked.
3. Double-click its shortcut, press the new combination, click Done.

This is a keyboard-shortcut change, so ask before guiding it. Offer Control+F (one easy press) and Control+Option+F (fewest clashes), and tell them the trade-offs plainly:
- Control+F normally moves the cursor forward one character in Mac text fields and Terminal. That stops working once reassigned. Few people use it.
- Never Command+F (that is Find).
- A yellow warning triangle in the settings list means a clash. Pick another.
- Control+G and Control+V also work, and each replaces a rarely used text-editing shortcut.
- Over Chrome Remote Desktop from a Windows laptop, the browser may catch Ctrl+F for its own Find bar. Full-screen mode often helps but not always. Otherwise use Control+Option+F.
- Have them test at the Mac itself first, then through Chrome Remote Desktop.

Do not write this setting with `defaults write`. Editing that preference by hand is fragile and may not take effect until logout. The user sets it in System Settings.

Verify: run the check command again (the setting can take a few seconds to show). Then have the user press the shortcut and paste into this chat with Cmd+V. If you receive an image of their screen, it works.

## Wrap up

1. If the user agreed to a progress note, update `mac-mini-setup-progress.md` with the final state using your file-editing tool. Otherwise summarize in the chat.
2. Give a short summary: what is confirmed working, what the user chose (FileVault and login), and anything still open.
3. Suggest the next step: Section F of the guide and the `session-handoff-60` or `session-refresh` skill from this library.

## If something does not work

- Ask for a screenshot first. It is faster than questions.
- Offline in Chrome Remote Desktop: Mac asleep, shut down, at the login screen, or off the network.
- Black screen or dead mouse over remote: most often a Privacy & Security permission, sometimes the host or a missing display. Have the user read any prompt on the Mac's screen, recheck Accessibility and Screen & System Audio Recording for the Chrome Remote Desktop entries only, then restart once. Do not have them reset or toggle unrelated permissions.
- "Automatically log in as" grayed out: usually FileVault is on. A managed Mac or an Apple Account based login password can also cause it.
- Still sleeping: rerun `pmset -g` and `pmset -g assertions`, and ask whether anyone used Apple menu > Sleep.
