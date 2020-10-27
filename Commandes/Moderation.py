import discord
from Fonctions import Erreur
from discord.ext import commands
from Classes.GestionnaireResources import GestionnaireResources

class Moderation(commands.Cog):
    def __init__(self, gestRes : GestionnaireResources):
        self.client = gestRes.client

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, p_nombreMessage: int = 5):
        if p_nombreMessage >= 100:
            return await ctx.send("You can't delete more than 100 messages.")
        await ctx.channel.purge(limit=p_nombreMessage+1)
