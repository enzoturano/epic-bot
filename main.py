import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ANNOUNCE_CHANNEL_ID = int(os.getenv('ANNOUNCE_CHANNEL_ID'))
MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
TEST_CHANNEL_ID = int(os.getenv('TEST_CHANNEL_ID'))

# Set up the bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
intents.reactions = True  # Enable reaction events

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension('cogs.slash_commands')
        # Sync commands to the specific guild
        guild = discord.Object(id=MAIN_GUILD_ID)
        await self.tree.sync(guild=guild)

# Initialize bot instance
bot = MyBot(command_prefix="!", intents=intents)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print("Epic! Bot is online!")
    channel = bot.get_channel(TEST_CHANNEL_ID)
    await channel.send("Epic! Bot is online!")
    
    # Set bot's activity status
    activity = discord.Game(name="Uzbadul Khazâd ai-menu, ganazul farnâkh râd, nadadûn ârakh Tûranor. \n - Bothûl")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("Slash commands synced")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use /announce to see the list of available commands.")
    else:
        await ctx.send(f"An error occurred: {error}")
        raise error  # Log the error to the console

# Run the bot
bot.run(BOT_TOKEN)
