# /mercado Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/mercado` slash command that lets any player anonymously post a buy/sell thread to the `#mercado` forum channel.

**Architecture:** Subclass `ConfirmButton` into a `ForumConfirmButton` that calls `create_thread()` instead of `send()`. Add a `forum=False` flag to the existing `send_dm()` helper to select which button class to use. Add the `/mercado` command wired to `MERCADO_CHANNEL_ID`.

**Tech Stack:** discord.py 2.5+, python-dotenv

---

### Task 1: Add `MERCADO_CHANNEL_ID` env variable

**Files:**
- Modify: `.env.example`
- Modify: `cogs/slash_commands.py:12-20`

- [ ] **Step 1: Add to `.env.example`**

Open `.env.example` and append:
```
MERCADO_CHANNEL_ID = 1480646545761374218
```

- [ ] **Step 2: Load the variable in `slash_commands.py`**

In `cogs/slash_commands.py`, find the `try` block that loads env vars (lines 12–20). Add `MERCADO_CHANNEL_ID` alongside the others:

```python
try:
    ANNOUNCE_CHANNEL_ID = int(os.getenv('ANNOUNCE_CHANNEL_ID'))
    BACKGROUNDS_CHANNEL_ID = int(os.getenv('BACKGROUNDS_CHANNEL_ID'))
    BUILDS_CHANNEL_ID = int(os.getenv('BUILDS_CHANNEL_ID'))
    MODERATION_CHANNEL_ID = int(os.getenv('MODERATION_CHANNEL_ID'))
    MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
    STAFF_CHANNEL_ID = int(os.getenv('STAFF_CHANNEL_ID'))
    STAFF_ANNOUNCE_CHANNEL_ID = int(os.getenv('STAFF_ANNOUNCE_CHANNEL_ID'))
    MERCADO_CHANNEL_ID = int(os.getenv('MERCADO_CHANNEL_ID'))
except TypeError:
    raise ValueError("One or more environment variables are missing or not set correctly.")
```

- [ ] **Step 3: Add `MERCADO_CHANNEL_ID` to your real `.env` file**

Open `.env` and add:
```
MERCADO_CHANNEL_ID = 1480646545761374218
```

- [ ] **Step 4: Commit**

```bash
git add .env.example cogs/slash_commands.py
git commit -m "feat: add MERCADO_CHANNEL_ID env variable"
```

---

### Task 2: Add `ForumConfirmButton` class

**Files:**
- Modify: `cogs/slash_commands.py` — add class after `ConfirmButton` (after line 58)

- [ ] **Step 1: Add `ForumConfirmButton` after the `ConfirmButton` class**

Insert the following class immediately after the closing of `ConfirmButton` (after line 58, before `class SlashCommands`):

```python
class ForumConfirmButton(ConfirmButton):
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("Você não pode confirmar isso.", ephemeral=True)
            return

        await interaction.response.send_message("A sua publicação foi confirmada e publicada!", ephemeral=True)

        files = [await f.to_file() for f in self.files] if self.files else []
        await self.target_channel.create_thread(
            name=self.embed.title,
            embed=self.embed,
            files=files,
        )

        await self.moderation_channel.send(
            f"{self.user.display_name} ({self.user.id}) postou um {self.title_type}."
        )

        self.stop()
```

- [ ] **Step 2: Verify the file still parses**

```bash
cd "C:/Projects/epic bot/epic-bot" && uv run python -c "import cogs.slash_commands"
```

Expected: no output, exit code 0.

- [ ] **Step 3: Commit**

```bash
git add cogs/slash_commands.py
git commit -m "feat: add ForumConfirmButton for forum channel posting"
```

---

### Task 3: Add `forum` parameter to `send_dm()`

**Files:**
- Modify: `cogs/slash_commands.py` — `send_dm` method signature and `ConfirmButton` instantiation

- [ ] **Step 1: Update the `send_dm` signature**

Find this line in `send_dm` (around line 93):
```python
async def send_dm(self, user: discord.User, channel_id: int, title_type: str, description_prompt: str, title_prompt: str, success_message: str):
```

Replace with:
```python
async def send_dm(self, user: discord.User, channel_id: int, title_type: str, description_prompt: str, title_prompt: str, success_message: str, forum: bool = False):
```

- [ ] **Step 2: Update the `ConfirmButton` instantiation inside `send_dm`**

Find this line (around line 124):
```python
view = ConfirmButton(user, embed, self.bot.get_channel(channel_id), self.bot.get_channel(MODERATION_CHANNEL_ID), self.bot, title_type, file_attachments)
```

Replace with:
```python
button_class = ForumConfirmButton if forum else ConfirmButton
view = button_class(user, embed, self.bot.get_channel(channel_id), self.bot.get_channel(MODERATION_CHANNEL_ID), self.bot, title_type, file_attachments)
```

- [ ] **Step 3: Verify the file still parses**

```bash
cd "C:/Projects/epic bot/epic-bot" && uv run python -c "import cogs.slash_commands"
```

Expected: no output, exit code 0.

- [ ] **Step 4: Commit**

```bash
git add cogs/slash_commands.py
git commit -m "feat: add forum parameter to send_dm helper"
```

---

### Task 4: Add `/mercado` command and register it

**Files:**
- Modify: `cogs/slash_commands.py` — `SlashCommands.__init__` and new command method

- [ ] **Step 1: Register the command in `__init__`**

Find `SlashCommands.__init__` (around line 62–68). Add the registration line:

```python
def __init__(self, bot):
    self.bot = bot
    self.bot.tree.add_command(self.announce, guild=discord.Object(id=MAIN_GUILD_ID))
    self.bot.tree.add_command(self.backgrounds, guild=discord.Object(id=MAIN_GUILD_ID))
    self.bot.tree.add_command(self.build, guild=discord.Object(id=MAIN_GUILD_ID))
    self.bot.tree.add_command(self.query, guild=discord.Object(id=MAIN_GUILD_ID))
    self.bot.tree.add_command(self.announce_staff, guild=discord.Object(id=MAIN_GUILD_ID))
    self.bot.tree.add_command(self.mercado, guild=discord.Object(id=MAIN_GUILD_ID))
```

- [ ] **Step 2: Add the `/mercado` command method**

Add the following method to `SlashCommands`, after `announce_staff` and before `send_dm`:

```python
@app_commands.command(name="mercado", description="Anuncia o que você quer vender ou comprar no #mercado")
async def mercado(self, interaction: discord.Interaction):
    await interaction.response.send_message("Olhe seu privado para continuarmos o anúncio.", ephemeral=True)
    await self.send_dm(
        interaction.user,
        MERCADO_CHANNEL_ID,
        "anúncio de mercado",
        "o que você quer vender ou comprar",
        "anúncio de mercado",
        "seu anúncio de mercado",
        forum=True,
    )
```

- [ ] **Step 3: Verify the file still parses**

```bash
cd "C:/Projects/epic bot/epic-bot" && uv run python -c "import cogs.slash_commands"
```

Expected: no output, exit code 0.

- [ ] **Step 4: Commit**

```bash
git add cogs/slash_commands.py
git commit -m "feat: implement /mercado command for forum channel"
```

---

### Task 5: Manual end-to-end verification

- [ ] **Step 1: Start the bot**

```bash
cd "C:/Projects/epic bot/epic-bot" && uv run main.py
```

Expected: bot comes online, `#test` channel receives "Epic! Bot is online!"

- [ ] **Step 2: Run `/mercado` in Discord**

In any channel, type `/mercado`. Expected: ephemeral reply "Olhe seu privado para continuarmos o anúncio."

- [ ] **Step 3: Complete the DM flow**

In the bot's DM, answer:
- Title: anything (e.g. `Vendo espada de ferro`)
- Description: anything (e.g. `Preço: 5 moedas de ouro`)
- Files: `nenhum`

Expected: preview embed appears with Confirm/Cancel buttons.

- [ ] **Step 4: Confirm and verify forum post**

Click Confirm. Expected:
- Bot DM: "A sua publicação foi confirmada e publicada!"
- `#mercado` forum channel: new thread created with the title and description from the form
- `MODERATION_CHANNEL_ID` channel: message with your display name and user ID
