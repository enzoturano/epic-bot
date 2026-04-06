# /anuncio-staff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/anuncio-staff` slash command that works like `/anuncio` but is restricted to World Builder and Admin roles and posts to a dedicated staff announcement channel.

**Architecture:** Add a new env var for the staff announcement channel, define the two allowed role IDs as constants in `slash_commands.py`, and add a new command handler that does an inline role check before delegating to the existing `send_dm()` method.

**Tech Stack:** Python 3.12, discord.py 2.5+, python-dotenv

---

### Task 1: Add environment variable

**Files:**
- Modify: `.env.example`
- Modify: `.env`

- [ ] **Step 1: Add `STAFF_ANNOUNCE_CHANNEL_ID` to `.env.example`**

Open `.env.example` and add this line at the end:

```
STAFF_ANNOUNCE_CHANNEL_ID=1488618798624805014
```

- [ ] **Step 2: Add the real value to `.env`**

Open `.env` and add this line at the end:

```
STAFF_ANNOUNCE_CHANNEL_ID=1488618798624805014
```

- [ ] **Step 3: Commit**

```bash
git add .env.example
git commit -m "feat: add STAFF_ANNOUNCE_CHANNEL_ID env variable"
```

(Do NOT stage `.env` — it is gitignored.)

---

### Task 2: Add constants and register command in `slash_commands.py`

**Files:**
- Modify: `cogs/slash_commands.py`

- [ ] **Step 1: Add `STAFF_ANNOUNCE_CHANNEL_ID` to the env var block**

In `cogs/slash_commands.py`, inside the `try` block that loads the other channel IDs (lines 12–18), add:

```python
STAFF_ANNOUNCE_CHANNEL_ID = int(os.getenv('STAFF_ANNOUNCE_CHANNEL_ID'))
```

The full `try` block should now look like:

```python
try:
    ANNOUNCE_CHANNEL_ID = int(os.getenv('ANNOUNCE_CHANNEL_ID'))
    BACKGROUNDS_CHANNEL_ID = int(os.getenv('BACKGROUNDS_CHANNEL_ID'))
    BUILDS_CHANNEL_ID = int(os.getenv('BUILDS_CHANNEL_ID'))
    MODERATION_CHANNEL_ID = int(os.getenv('MODERATION_CHANNEL_ID'))
    MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
    STAFF_CHANNEL_ID = int(os.getenv('STAFF_CHANNEL_ID'))
    STAFF_ANNOUNCE_CHANNEL_ID = int(os.getenv('STAFF_ANNOUNCE_CHANNEL_ID'))
except TypeError:
    raise ValueError("One or more environment variables are missing or not set correctly.")
```

- [ ] **Step 2: Add the role ID constant after the `try/except` block**

Immediately after the `except` block, add:

```python
ALLOWED_STAFF_ROLES = {1261474104301850675, 1261348549824876544}  # World Builder, Admin
```

- [ ] **Step 3: Register the new command in `SlashCommands.__init__`**

Inside `SlashCommands.__init__`, add a line after the existing `self.bot.tree.add_command(self.query, ...)` call:

```python
self.bot.tree.add_command(self.announce_staff, guild=discord.Object(id=MAIN_GUILD_ID))
```

The full `__init__` should now look like:

```python
def __init__(self, bot):
    self.bot = bot
    self.bot.tree.add_command(self.announce, guild=discord.Object(id=MAIN_GUILD_ID))
    self.bot.tree.add_command(self.backgrounds, guild=discord.Object(id=MAIN_GUILD_ID))
    self.bot.tree.add_command(self.build, guild=discord.Object(id=MAIN_GUILD_ID))
    self.bot.tree.add_command(self.query, guild=discord.Object(id=MAIN_GUILD_ID))
    self.bot.tree.add_command(self.announce_staff, guild=discord.Object(id=MAIN_GUILD_ID))
```

- [ ] **Step 4: Commit**

```bash
git add cogs/slash_commands.py
git commit -m "feat: register /anuncio-staff command and add role/channel constants"
```

---

### Task 3: Implement the command handler

**Files:**
- Modify: `cogs/slash_commands.py`

- [ ] **Step 1: Add the command method to the `SlashCommands` class**

Add this method to the `SlashCommands` class, after the `build` method and before `send_dm`:

```python
@app_commands.command(name="anuncio-staff", description="Envia um anúncio no canal de staff (apenas Staff)")
async def announce_staff(self, interaction: discord.Interaction):
    user_role_ids = {role.id for role in interaction.user.roles}
    if not user_role_ids & ALLOWED_STAFF_ROLES:
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
        return
    await interaction.response.send_message("Olhe seu privado para continuarmos o anuncio.", ephemeral=True)
    await self.send_dm(interaction.user, STAFF_ANNOUNCE_CHANNEL_ID, "anúncio", "o anúncio", "anúncio", "seu anúncio")
```

- [ ] **Step 2: Verify the bot starts without errors**

Run:
```bash
uv run main.py
```

Expected: Bot starts, prints no errors, and sends the "Epic! Bot is online!" message to the test channel.

- [ ] **Step 3: Verify the command appears in Discord**

In the Discord server, type `/anuncio-staff` — it should appear as a slash command option.

- [ ] **Step 4: Test role restriction**

With a user that does NOT have World Builder or Admin roles, invoke `/anuncio-staff`.
Expected: ephemeral message "Você não tem permissão para usar este comando."

- [ ] **Step 5: Test successful flow**

With a user that HAS World Builder or Admin role, invoke `/anuncio-staff` and complete the DM flow.
Expected: announcement posted to channel `1488618798624805014`, moderation log entry sent to `MODERATION_CHANNEL_ID`.

- [ ] **Step 6: Commit**

```bash
git add cogs/slash_commands.py
git commit -m "feat: implement /anuncio-staff command with role restriction"
```
