import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ANNOUNCE_CHANNEL_ID = int(os.getenv('ANNOUNCE_CHANNEL_ID'))
MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
TEST_CHANNEL_ID = int(os.getenv('TEST_CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension('cogs.slash_commands')
        guild = discord.Object(id=MAIN_GUILD_ID)
        await self.tree.sync(guild=guild)

bot = MyBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    channel = bot.get_channel(TEST_CHANNEL_ID)
    await channel.send("Epic! Bot is online!")
    activity = discord.Game(name="Epic! Shard")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando não encontrado. Use !comandos para ver a lista de comandos disponíveis.")
    else:
        await ctx.send(f"Ocorreu um erro: {error}")
        raise error

bot.run(BOT_TOKEN)
