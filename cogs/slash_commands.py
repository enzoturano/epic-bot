import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import os
from dotenv import load_dotenv

load_dotenv()

try:
    ANNOUNCE_CHANNEL_ID = int(os.getenv('ANNOUNCE_CHANNEL_ID'))
    BACKGROUNDS_CHANNEL_ID = int(os.getenv('BACKGROUNDS_CHANNEL_ID'))
    BUILDS_CHANNEL_ID = int(os.getenv('BUILDS_CHANNEL_ID'))
    MODERATION_CHANNEL_ID = int(os.getenv('MODERATION_CHANNEL_ID'))
    MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
except TypeError:
    raise ValueError("One or more environment variables are missing or not set correctly.")

class ConfirmButton(View):
    def __init__(self, user, embed, target_channel, moderation_channel, bot, title_type, files):
        super().__init__(timeout=60) 
        self.user = user
        self.embed = embed
        self.target_channel = target_channel
        self.moderation_channel = moderation_channel
        self.bot = bot
        self.title_type = title_type
        self.files = files

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("Você não pode confirmar isso.", ephemeral=True)
            return

        await interaction.response.send_message("A sua publicação foi confirmada e publicada!", ephemeral=True)
        await self.target_channel.send(embed=self.embed)
        
        if self.files:
            await self.target_channel.send(files=[await file.to_file() for file in self.files])

        await self.moderation_channel.send(f"{self.user.display_name} ({self.user.id}) postou um {self.title_type}.")
        
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("Você não pode cancelar essa mensagem.", ephemeral=True)
            return
        
        await interaction.response.send_message("Sua publicação foi cancelada.", ephemeral=True)
        self.stop()

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.announce, guild=discord.Object(id=MAIN_GUILD_ID))
        self.bot.tree.add_command(self.backgrounds, guild=discord.Object(id=MAIN_GUILD_ID))
        self.bot.tree.add_command(self.build, guild=discord.Object(id=MAIN_GUILD_ID))

    @app_commands.command(name="anuncio", description="Envia um anúncio RP no #anuncios-roleplay")
    async def announce(self, interaction: discord.Interaction):
        await interaction.response.send_message("Olhe seu privado para continuarmos o anuncio.", ephemeral=True)
        await self.send_dm(interaction.user, ANNOUNCE_CHANNEL_ID, "anúncio", "o anúncio", "anúncio", "seu anúncio")

    @app_commands.command(name="background", description="Envia o background do seu personagem no #epic-backgrounds")
    async def backgrounds(self, interaction: discord.Interaction):
        await interaction.response.send_message("Olhe seu privado para continuarmos a postagem.", ephemeral=True)
        await self.send_dm(interaction.user, BACKGROUNDS_CHANNEL_ID, "background", "a história do seu personagem", "personagem", "seu background")

    async def send_dm(self, user: discord.User, channel_id: int, title_type: str, description_prompt: str, title_prompt: str, success_message: str):
        def check(m):
            return m.author == user and isinstance(m.channel, discord.DMChannel)
        
        try:
            dm_channel = await user.create_dm()
            
            await dm_channel.send(f"Me diga o nome do seu {title_prompt}:")
            announcement_name = await self.bot.wait_for('message', check=check)
            
            await dm_channel.send(f"Agora {description_prompt}:")
            announcement_description = await self.bot.wait_for('message', check=check)
            
            await dm_channel.send("Se quiser incluir algum arquivo, essa é a hora (ou digite 'nenhum'):")
            files_to_include = await self.bot.wait_for('message', check=check)
            
            file_urls = []
            file_attachments = []

            if files_to_include.content.lower() != 'nenhum':
                if files_to_include.attachments:
                    file_attachments = files_to_include.attachments
                else:
                    file_urls = files_to_include.content.split()

            embed = discord.Embed(title=announcement_name.content, description=announcement_description.content, color=discord.Color.red())
            
            if file_urls:
                for url in file_urls:
                    embed.add_field(name="File URL", value=url, inline=False)

            view = ConfirmButton(user, embed, self.bot.get_channel(channel_id), self.bot.get_channel(MODERATION_CHANNEL_ID), self.bot, title_type, file_attachments)
            await dm_channel.send("Aqui está uma prévia da sua publicação:", embed=embed, view=view)
            
            if file_attachments:
                await dm_channel.send("Esses são os arquivos que você anexou:", files=[await file.to_file() for file in file_attachments])

        except Exception as e:
            await dm_channel.send(f"Ocorreu um erro: {e}")

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
