# Design: /anuncio-staff Command

**Date:** 2026-04-06
**Status:** Approved

## Overview

Add a `/anuncio-staff` slash command to the Bothûl bot. It works identically to `/anuncio` but is restricted to users with specific staff roles and publishes to a dedicated staff announcement channel.

## Requirements

- Only users with the **World Builder** (ID: `1261474104301850675`) or **Admin** (ID: `1261348549824876544`) role can invoke the command.
- Announcements are published to channel ID `1488618798624805014`.
- The DM-based collection flow, preview embed, `ConfirmButton`, and moderation log are reused unchanged from the existing `/anuncio` implementation.

## Changes

### `.env` and `.env.example`

Add:
```
STAFF_ANNOUNCE_CHANNEL_ID=1488618798624805014
```

### `cogs/slash_commands.py`

**New constants** (top of file, alongside existing channel ID loads):
```python
STAFF_ANNOUNCE_CHANNEL_ID = int(os.getenv('STAFF_ANNOUNCE_CHANNEL_ID'))
ALLOWED_STAFF_ROLES = {1261474104301850675, 1261348549824876544}  # World Builder, Admin
```

**Load channel in `__init__`** — register the new command on `MAIN_GUILD_ID`:
```python
self.bot.tree.add_command(self.announce_staff, guild=discord.Object(id=MAIN_GUILD_ID))
```

**New command handler:**
```python
@app_commands.command(name="anuncio-staff", description="Envia um anúncio no canal de staff")
async def announce_staff(self, interaction: discord.Interaction):
    user_role_ids = {role.id for role in interaction.user.roles}
    if not user_role_ids & ALLOWED_STAFF_ROLES:
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
        return
    await interaction.response.send_message("Olhe seu privado para continuarmos o anuncio.", ephemeral=True)
    await self.send_dm(interaction.user, STAFF_ANNOUNCE_CHANNEL_ID, "anúncio", "o anúncio", "anúncio", "seu anúncio")
```

## What is NOT changed

- `send_dm()` — reused as-is
- `ConfirmButton` — reused as-is
- Moderation log — still posts to `MODERATION_CHANNEL_ID`
- `main.py` — no changes needed
