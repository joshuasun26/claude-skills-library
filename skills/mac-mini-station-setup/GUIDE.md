# Mac mini AI Station: Setup Guide

This guide sets up a Mac mini (or any Mac you can leave plugged in) as an always-on AI station. It sits on a desk, stays awake, and you reach it from your laptop or your phone whenever you want. Claude still needs the app open, your account signed in, an internet connection, and a task from you.

**How long:** allow an hour or two, plus extra time for downloads and copying files.

**A note on the folder name:** this guide calls your working folder `ai-workspace`. That is just an example name. Use whatever your own working folder is called.

**What you need:**
- The Mac mini, plugged in, with a monitor, keyboard and mouse attached for the setup (you can unplug the monitor afterward, see the note in Section C)
- Your laptop
- Your Claude account (a paid plan that includes Claude Code)
- A Google account (for Chrome Remote Desktop and Google Drive)

**How to use this guide:** go in order, A through F, and tick each box as you finish it. Menu names are from current macOS (Sequoia and Tahoe). Apple moves things around between versions, so where a label on your screen does not match exactly, use the search box at the top of System Settings and type the word in quotes.

**Shortcut:** this skill folder also includes a Claude skill (`SKILL.md`) that walks you through Sections A to E one step at a time and checks your settings for you. Once Claude is installed (Section B), see this skill's README.md for how to add it, then type: `walk me through the Mac mini setup`.

---

## Section A: Make the Mac mini always on

**Why:** Claude can only work, and you can only connect, while the Mac mini is awake. A sleeping Mac is an unreachable Mac. The screen can go dark. The computer itself must not sleep.

### A1. Stop it from sleeping

1. [ ] Click the Apple menu (top left corner) and choose **System Settings**.
2. [ ] In the left sidebar, click **Energy**. (On a Mac mini it is called Energy. On a laptop the same area is called Battery.)
3. [ ] Turn ON **Prevent automatic sleeping when the display is off**.
4. [ ] Turn ON **Wake for network access**.
5. [ ] Find the power-recovery setting. On some Macs it is a switch called **Start up automatically after a power failure**: turn it ON. On others it is a menu called **Start up when power is connected**: choose **After power failure**. Which one you see depends on the Mac model and macOS version.
6. [ ] If you see **Put hard disks to sleep when possible**, turn it OFF. (Optional. It mostly matters for external drives.)

### A2. Let the display turn off (this is fine)

The display going dark saves power and does not stop Claude.

1. [ ] In System Settings, click **Lock Screen**.
2. [ ] Find the display-off timer. Look for **Turn display off when inactive** (the label may include "on power adapter"). Set it to whatever you like, for example 10 minutes.
3. [ ] Leave the password requirement on this page at a setting you are comfortable with. A screen saver is fine too. Neither one puts the computer to sleep.

### A3. Decide about automatic login

**Why it matters:** if the power blinks and the Mac mini restarts, it stops and waits for your password. Until someone logs in, Claude is not running and Remote Control will not work.

There are two ways to handle this. Pick one.

**Choice 1 (recommended): keep FileVault on and log in by hand after a restart.**
- FileVault is a macOS security feature that ties the Mac's storage to your login password. On new Macs it is often already on.
- With FileVault on, macOS does not allow automatic login. After a cold start or a power failure, plan for someone to type the password at the Mac mini itself. Chrome Remote Desktop cannot reach the Mac until that first unlock is done.
- A locked screen on a Mac that is already running is different. You can usually still connect remotely and type your password there.
- Restarts are rare (power failures and system updates), so many people accept this.
- [ ] If you choose this, do nothing here. Just remember: after a restart, log in at the Mac mini itself.

**Choice 2 (more convenient, less secure): turn on automatic login.**
- This only works if FileVault is off. Two things change. First, you give up the protection FileVault adds on top of the Mac's built-in storage encryption. Second, anyone with physical access can start the Mac straight into your account, with your files and signed-in apps, without typing a password.
- Think about what is reachable on this Mac before choosing convenience. This is your decision. Do not let any tool or assistant make it or click it for you.
- To check FileVault: System Settings > **Privacy & Security**, scroll down to **FileVault**.
- [ ] If FileVault is off (or you chose to turn it off), go to System Settings > **Users & Groups**.
- [ ] Find **Automatically log in as** and choose your user. Type your password when asked.
- If that option is grayed out, the usual cause is that FileVault is on. A work-managed Mac, or a login password tied to your Apple Account, can also block it.

Advanced note: macOS Tahoe 26 on Apple silicon can unlock FileVault over the network after a restart if Remote Login (SSH) was set up beforehand. That is a separate project with its own security questions and is not part of this guide.

### A4. Power and network

1. [ ] Plug the Mac mini straight into a wall outlet or a surge protector that nobody switches off. A small battery backup (UPS) is a nice extra if your power flickers.
2. [ ] If you can, run an ethernet cable from the Mac mini to your router. Wired is steadier than Wi-Fi for a machine that is on all day. Wi-Fi works if a cable is not practical.

### A5. The one thing nobody should click

- [ ] Tell everyone in the house: on this Mac, never click **Apple menu > Sleep**, and do not press the power button.

There is no setting that removes the Sleep menu item. If someone puts the Mac to sleep by hand, remote access may stop, and "Wake for network access" is not a reliable way to get it back. Someone would have to tap the keyboard or mouse. A sticky note on the Mac mini that says "Always on. Do not sleep or shut down." is a real solution.

### A6. Quick check

- [ ] Come back to this check after Sections B and C are done. Leave the Mac mini untouched for longer than your display-off timer. Then, before touching its mouse or keyboard, connect from your laptop and send a message to your Claude session. If both Remote Control and Chrome Remote Desktop still work, the always-on setup is good. Do not pull the power cord to test it.

---

## Section B: Install the Claude desktop app and turn on Remote Control

**Why:** the Claude desktop app is where Claude Code runs. Remote Control lets you see and steer those same sessions from your laptop browser or your phone, while the work itself stays on the Mac mini.

### B1. Install and sign in

1. [ ] On the Mac mini, open Safari and go to **claude.ai/download**.
2. [ ] Download the macOS version. Open the downloaded file and drag **Claude** into the **Applications** folder.
3. [ ] Open Claude from Applications. If macOS asks whether you are sure you want to open it, click **Open**.
4. [ ] Sign in with your Claude account.

### B2. Open your working folder in Claude Code

1. [ ] In the Claude app, look for the **Code** tab (near the top of the window or in the sidebar).
2. [ ] Start a new session. When it asks which folder to work in, choose your **ai-workspace** folder. If the folder is not on the Mac mini yet, do Section D first, then come back to this step.
3. [ ] Type a first message such as `List the top-level folders here and tell me what you see. Do not change anything.` to confirm Claude can see your files.

If macOS asks whether Claude may access a folder, click **Allow**.

### B3. Turn on Remote Control

1. [ ] In the Code session you just opened on the Mac mini, look for a **Remote Control** switch for that session and turn it on. If you cannot find one, type `/remote-control` in the message box and follow what it says.
2. [ ] To make every new session reachable without repeating step 1, open the Claude app's **Settings** (Claude menu at the top of the screen > Settings, or press Cmd+comma). Look for the **Code** section (called Claude Code in some versions), then look for an option like **Connect new sessions to Remote Control** and turn it on.
3. [ ] Labels shift between app versions. If yours looks different, ask Claude: `How do I turn on Remote Control in this app?`

### B4. Keep the computer awake while Claude works

1. [ ] In the same Settings area, look for **Keep computer awake while Claude works** and turn it on. If your version does not show it, skip this step.

This is a second safety net. Section A is still the main protection.

### B5. Test from your laptop and phone

1. [ ] On your laptop, open a browser and go to **claude.ai/code**. Sign in with the same Claude account. Your Mac mini session should be in the list. Open it and send a message.
2. [ ] On your phone, open the **Claude** app, sign in with the same account, and look for the **Code** section. Open the same session there.

Remote Control only works while the Claude app is open on the Mac mini and the Mac is awake and logged in. That is the whole reason for Section A.

- [ ] Optional but smart: make Claude open by itself after you log in. Right-click the Claude icon in the Dock > **Options** > **Open at Login**.

Open at Login only launches the app. It does not pick unfinished work back up. After any restart, check four things: the Mac is logged in, Claude is open, your main session is connected to Remote Control, and any scheduled tasks are still on.

---

## Section C: Chrome Remote Desktop (see the Mac mini's whole screen)

**Why:** Remote Control shows you Claude. Chrome Remote Desktop shows you the entire Mac mini screen, so you can click around in any app, approve a pop-up, or fix something, all from your laptop. It is free.

### C1. Install the host on the Mac mini

1. [ ] On the Mac mini, install **Google Chrome** if it is not there yet (google.com/chrome).
2. [ ] In Chrome, sign in to your Google account and go to **remotedesktop.google.com/access**.
3. [ ] Under **Set up remote access**, click the download button (a blue circle with a down arrow).
4. [ ] It downloads an installer package. Open it and click through the installer. Type your Mac password when asked.
5. [ ] Back on the web page, click **Turn On** if it shows. Give the computer a name, for example `Office Mac mini`.
6. [ ] Choose a **PIN** of at least 6 digits. Pick one you do not use anywhere else, and do not share it. Anyone with your Google account and this PIN can control the Mac.

### C2. Give it the macOS permissions it needs

macOS will not let any app view or control the screen until you approve it. Chrome Remote Desktop will prompt you during setup. Follow its prompts first. The steps below are where those prompts lead, and where to look if you missed one.

1. [ ] Open System Settings > **Privacy & Security**.
2. [ ] Click **Accessibility**. Turn ON the Chrome Remote Desktop entry. It is usually named **ChromeRemoteDesktopHost**. This lets it move the mouse and type.
3. [ ] Go back and click **Screen & System Audio Recording** (on some versions it is just called Screen Recording). Turn ON the Chrome Remote Desktop entry. Here the name can look different: it may show as **ChromeRemoteDesktopHost** or as a technical name such as `org.chromium.chromoting.me2me.sh`. This lets it show you the screen.
4. [ ] **Input Monitoring:** turn this on for Chrome Remote Desktop only if the setup asks you for it. If it never asks, leave it alone.
5. [ ] If macOS says the app must be quit and reopened for the change to take effect, agree, then go back to the setup page and finish.

These are security permissions. Approve them yourself, on purpose, and only for the Chrome Remote Desktop entries that match what the installer asked for. Do not approve an unrelated app with a similar name.

### C3. Connect from your laptop

1. [ ] On your laptop, open Chrome and go to **remotedesktop.google.com/access**.
2. [ ] Sign in with the **same Google account** you used on the Mac mini.
3. [ ] Click your Mac mini in the list and type your PIN.
4. [ ] You should now see the Mac mini's desktop inside the browser tab.

### C4. Tips that make it comfortable

Once connected, there is a small arrow tab on the right edge of the window. Click it to open the options panel.

- [ ] **Full-screen:** turn this on so the Mac fills your laptop screen. More keyboard shortcuts pass through to the Mac in this mode, though not always every one.
- [ ] **Scale to fit / Resize to fit:** turn these on if the picture looks too small or too big.
- [ ] **Configure key mappings:** look for this if your laptop is a Windows PC. First test copy and paste as is: the Windows key usually acts as Command. If that feels awkward, you can map a key you do not use much (many people pick the right Ctrl key) to act as Command. The panel shows the exact key names to type.
- [ ] **Clipboard:** look for a clipboard sync option and allow it, so you can copy text on the laptop and paste it on the Mac, and the other way around. Text is dependable. Do not count on images crossing over.
- [ ] For an app-like window with fewer browser distractions, look for the install icon at the right end of Chrome's address bar and install Chrome Remote Desktop as an app.

**Note about unplugging the monitor:** a Mac mini with no display attached sometimes shows a small or low-resolution remote screen. If that happens, try the scale and resize options first. If that is not enough, leave a monitor connected (it can be asleep), or consider an inexpensive "HDMI dummy plug," which makes the Mac think a monitor is attached. Results vary by Mac.

---

## Section D: Put your ai-workspace folder on the Mac mini

**Why:** Claude works best when everything it needs lives in one folder on the machine where it runs. The Mac mini copy becomes the "home" copy. You do your work there (through Remote Control or Chrome Remote Desktop), not in separate copies scattered across devices.

### Where the folder should live

Put it in your home folder, like this: `/Users/yourname/ai-workspace`.

Do not put the working copy inside Desktop or Documents if iCloud Drive is syncing those, and do not have Claude work directly inside a cloud-synced folder. Sync services can pause, duplicate or "offload" files while Claude is in the middle of editing them.

### Before you copy anything: a two-minute privacy check

- [ ] Look through the folder first. If it holds passwords, API keys, login tokens, files named `.env`, or client and financial information that should not sit in a cloud account, leave those out of any upload, or use AirDrop or a USB drive instead (see the end of this section). Those two never leave your hands.
- [ ] Keep the original on your laptop untouched until you have confirmed the Mac mini copy is complete.

### The recommended path: move it with Google Drive, then keep it local

This is the simplest path if your folder is on your laptop today.

1. [ ] On your laptop, go to **drive.google.com**, and drag your whole ai-workspace folder into the browser window to upload it. Wait until the upload finishes.
2. [ ] On the Mac mini, open **drive.google.com** in Chrome, find the folder, right-click it and choose **Download**. Google gives you one or more zip files.
3. [ ] Open the Downloads folder on the Mac mini and double-click each zip file to unpack it. If there was more than one zip, combine the pieces into a single folder.
4. [ ] Open Finder, press **Cmd+Shift+H** to jump to your home folder, and drag the unpacked folder there. Rename it to `ai-workspace` if needed.
5. [ ] Spot check: open a few subfolders and files you know well, and make sure they are all there.
6. [ ] In the Claude app, open this folder as your working folder (Section B2).

If you prefer the **Google Drive for desktop** app (google.com/drive/download), that works for the move as well: install it on both computers, let the folder sync, then copy the folder out of Google Drive into your home folder on the Mac mini. Keep the working copy outside the Google Drive folder for the reason above.

### Then: back it up

One copy on one machine is not a backup. Pick one:

- [ ] **Simple:** once a week, ask Claude: `Zip my ai-workspace folder and tell me where the zip is`, then upload that zip to Google Drive. Or turn on Time Machine with an external drive (System Settings > General > Time Machine).
- [ ] **Better, and Claude does the work:** a private GitHub repository. Create a free account at github.com, then tell Claude: `First inspect this folder, including hidden files, for passwords, keys, tokens, .env files and private client information. Tell me only the file paths and what kind of problem each one is, never the secret values themselves. Show me the list of what you would back up and what you would leave out. Do not create a repository or upload anything yet. After I approve the list, set up git and a PRIVATE GitHub repository and push only the approved files. I will type any passwords myself.` After that, you can say `commit and push my changes` any time, and you get a full history of every change. Two things to know: "private" means only you can see it, but the files still live on GitHub's servers, and git only backs up the files it tracks, so ask Claude what it left out.

Do the same privacy check before any cloud backup, including the weekly zip. If some files are too sensitive for a cloud account, back those up to an external drive with Time Machine instead.

### Other ways to copy (if Google Drive is not convenient)

- **AirDrop** (both machines are Macs and near each other): right-click the folder on your laptop > Share > AirDrop > choose the Mac mini. Good for small and medium folders.
- **USB drive:** copy the folder to the drive, plug it into the Mac mini, drag it to your home folder. Best for very large folders.

---

## Section E: One-press screenshot, straight to the clipboard

**Why:** the fastest way to show Claude what you are looking at is a picture of your screen. With this set up, it is two moves: one shortcut to capture the whole screen, then **Cmd+V** to paste it into Claude. No files to find or attach.

On a Mac, paste is **Cmd+V** (not Ctrl+V like on Windows).

### E1. Find the setting

1. [ ] On the Mac mini, open System Settings > **Keyboard**.
2. [ ] Click the **Keyboard Shortcuts...** button.
3. [ ] In the list on the left, click **Screenshots**.
4. [ ] Find the line **Copy picture of screen to the clipboard**. Its default shortcut is **Control+Shift+Command+3**, which is a handful. Make sure its checkbox is ticked.

### E2. Change it to something easy

1. [ ] Double-click the shortcut on the right side of that line. It turns into an editable box.
2. [ ] Press the new key combination you want. A good choice is **Control+F**, because it is one easy press and close to the paste keys. Read the trade-offs in E3 before you settle on it.
3. [ ] Click **Done**.

### E3. Know the trade-offs before you pick

- **Control+F** normally moves the text cursor forward one character in Mac text boxes and in Terminal. Few people use that, but once you assign it to screenshots, it stops doing that everywhere.
- **Do not use Command+F.** That is Find in nearly every app, and you would lose it.
- If macOS shows a yellow warning triangle next to your shortcut, it clashes with another system shortcut. Choose a different one.
- The pick with the fewest clashes is **Control+Option+F**. It is one more key, but almost nothing else uses it. Control+G and Control+V also work, and each one replaces a rarely used text-editing shortcut the same way Control+F does.
- A single key with no modifier (just F by itself) is not allowed for this, and you would not want it anyway.
- When you are connected through Chrome Remote Desktop **from a Windows laptop**, pressing Ctrl+F on the laptop may open Chrome's own Find bar instead of reaching the Mac. Full-screen mode (Section C4) often fixes that, but not always. If it does not, use Control+Option+F.
- Test your choice twice: once at the Mac mini itself, and once through Chrome Remote Desktop.

### E4. Test it

1. [ ] Press your new shortcut once. You may hear a camera click. Nothing else visible happens, and that is correct: the picture is on the clipboard.
2. [ ] Click into the Claude message box and press **Cmd+V**. The screenshot should appear, ready to send.

The screenshot is taken on whichever computer runs the shortcut. If you are remoted into the Mac mini, take it and paste it inside that remote window, so the capture and the paste both happen on the Mac mini.

A whole-screen capture shows everything on the screen. Before you paste one, glance at it for private messages, account details or login codes that Claude does not need to see.

---

## Section F: The chief-of-staff handoff habit

**Why:** if you keep one main Claude session open all day as your "chief of staff," it slowly fills up its working memory, which Claude calls context. As it fills, Claude starts summarizing older parts of the conversation, and details from earlier in the day can get lost. Long sessions also tend to get slower.

The fix is a simple habit: **at about 50% context, hand off to a fresh session.** Fifty percent is a comfortable margin, not a hard technical limit. (Context is how full one conversation is. It is not the same thing as your plan's usage limit.)

### What a handoff is

1. Claude writes a short handoff file. It covers:
   - open loops (what is in progress and what is next)
   - running jobs and where their results will show up
   - scheduled reminders and recurring tasks, and which of them live only inside this session and would need to be moved
   - pending asks (decisions waiting on you, things you are waiting on from others)
2. Claude starts a fresh session whose first instruction is to read that file. If your setup does not let Claude start sessions, follow the fallback described in the skill.
3. Claude pins the new session and unpins the old one (or asks you to), so the session at the top of your sidebar is always the current one.

Nothing is deleted. The old session stays in your history.

### How the included skill does it

The `session-handoff-60` skill in this library teaches Claude this routine (set `threshold_percent` to `50` in its config to match this guide). If you would rather refresh in place than start new sessions, use `session-refresh` instead. Install one of the two, not both.

- [ ] Install the skill.
- [ ] Give your main session a name with the date and time, for example `Main 11-17 9AM`, and pin it.
- [ ] Tell your main session once: `Use the handoff skill. Check context when I message you and hand off at 50%.`
- [ ] Any time you want to do it right away, type: `handoff now`.

To see how full a session is, type `/context` in the session. If your version does not have that command, just ask: `How full is your context?`

If Claude cannot start the new session by itself (this can happen when you are driving it from your phone), it still writes the handoff file and gives you a short message to paste into a new session.

One thing to understand: a skill is a set of instructions, not a program running in the background. Claude checks context when you send it a message. It will not hand off while you are away and nothing is happening.

The handoff never sends emails, texts or posts. Scheduled tasks you created in the app's own scheduler keep running by themselves and are left alone. Only reminders that live inside the old session get moved, one at a time, and only after the new session is confirmed up and running, so nothing fires twice and nothing gets dropped.

**A good rhythm:** one main session per work block, handed off at 50%, plus separate short sessions for big one-off projects so they do not fill up your main one.

---

## Troubleshooting

**The Mac mini does not show up in Chrome Remote Desktop, or says offline.**
- It may be asleep, shut down, or sitting at the login screen after a restart. Go to the Mac, wake it, and log in.
- Check its internet connection.
- Recheck Section A1. Then open remotedesktop.google.com/access on the Mac mini itself and confirm remote access is still turned on.

**I connect, but the screen is black or the mouse and keyboard do nothing.**
- Most often a permission from Section C2. Recheck Accessibility and Screen & System Audio Recording for the Chrome Remote Desktop entries, and look for any new prompt on the Mac mini's own screen.
- If the permissions look right, restart the Mac mini once. With no monitor attached, also see the display note at the end of Section C.
- After a macOS update, you may need to approve these again.

**macOS keeps asking whether Chrome Remote Desktop can keep recording the screen.**
- Recent macOS versions sometimes re-ask for screen recording approval. Approve it when you see it. If you are remote and cannot click it, you will need to do it at the Mac itself.

**The remote screen is tiny or blurry with no monitor attached.**
- See the note at the end of Section C: leave a monitor attached or use an HDMI dummy plug.

**My session does not appear at claude.ai/code or in the phone app.**
- The Claude app must be open on the Mac mini, and you must be signed in to the same Claude account everywhere.
- Confirm Remote Control is on (Section B3) for that session.
- Confirm the Mac is awake and online.

**The power went out and now nothing connects.**
- The Mac restarted and is waiting for your password (this is the FileVault trade-off in Section A3). Log in at the Mac. Then open the Claude app if it did not open by itself, and check that your session and any scheduled tasks are back.

**"Automatically log in as" is grayed out.**
- Usually FileVault is on. See Section A3 for the two choices. A work-managed Mac or a login password tied to your Apple Account can also block it.

**The Mac still seems to sleep.**
- Recheck Section A1. Then ask Claude on the Mac mini: `Run pmset -g and tell me if this Mac can sleep by itself`. In the result, the line `sleep` should show `0`.
- Make sure nobody used Apple menu > Sleep.

**The Mac restarted by itself overnight.**
- A restart can have several causes. A system update is a common one. Look at System Settings > General > Software Update, then the small "i" button next to Automatic Updates, to see what installs by itself, and look for any error message on the screen. Keep security updates on, and check your remote access and sessions after any restart.

**My screenshot shortcut does nothing.**
- Go back to Section E1 and confirm the checkbox on that line is ticked and there is no yellow warning triangle.
- Over Chrome Remote Desktop, try full-screen mode, or pick a shortcut the browser does not grab.
- Remember that nothing visible happens when it works. Test by pasting with Cmd+V.

**Paste puts in old text instead of my screenshot.**
- Either the shortcut did not fire, or the screenshot was taken on a different computer than the one you are pasting on. Test the capture and the paste at the Mac mini itself first, then inside the remote window.

**I got stuck somewhere else.**
- Take a screenshot (now you know how), check it for anything private, paste it into Claude, and ask: `What am I looking at and what should I click?`
