# /mercado Command — Design Spec

**Date:** 2026-04-12

## Overview

Add a `/mercado` slash command that lets any player anonymously post a buy/sell announcement to the `#mercado` forum channel. The player's identity is hidden from other players and only logged to `MODERATION_CHANNEL_ID` for staff accountability.

## User Flow

1. Player runs `/mercado` in any channel.
2. Bot replies ephemerally: `"Olhe seu privado para continuarmos o anúncio."`
3. Bot DMs the player three prompts in sequence:
   - `"Me diga o título do seu anúncio de mercado:"` → forum thread title
   - `"Agora descreva o que você quer vender ou comprar:"` → thread body
   - `"Se quiser incluir alguma imagem, essa é a hora (ou digite 'nenhum'):"` → optional attachment
4. Bot shows a preview embed with Confirm/Cancel buttons (60s timeout).
5. On **Confirm**: bot creates a thread in `#mercado`, logs the author to `MODERATION_CHANNEL_ID`.
6. On **Cancel**: bot sends cancellation message, stops.

No content restrictions — players self-moderate.

## Technical Design

### Environment

New variable added to `.env.example` and loaded in `slash_commands.py`:

```
MERCADO_CHANNEL_ID = 1480646545761374218
```

### `ForumConfirmButton` (new class)

Subclass of `ConfirmButton`. Overrides only the `confirm` button handler:

- Calls `target_channel.create_thread(name=self.embed.title, embed=self.embed, files=[...])` instead of `send()`
- All other behavior (cancel, user check, moderation log, timeout) inherited unchanged

### `send_dm()` change

Adds a `forum: bool = False` parameter. When `True`, instantiates `ForumConfirmButton` instead of `ConfirmButton`. No other logic changes.

### `/mercado` command

- Registered in `SlashCommands.__init__` and `setup_hook` alongside existing commands
- Calls `send_dm(user, MERCADO_CHANNEL_ID, "anúncio de mercado", "o que você quer vender ou comprar", "anúncio de mercado", "seu anúncio de mercado", forum=True)`

### No changes to existing commands

`ConfirmButton`, `/anuncio`, `/background`, `/build`, `/anuncio-staff` are untouched.

## Files Changed

| File | Change |
|---|---|
| `.env.example` | Add `MERCADO_CHANNEL_ID` |
| `cogs/slash_commands.py` | Add `ForumConfirmButton`, update `send_dm`, add `/mercado` command |
