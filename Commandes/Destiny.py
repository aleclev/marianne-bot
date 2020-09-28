"""
Contient l'implémantation des commandes de Destiny.
"""

import discord
from Fonctions import Erreur
from discord.ext import commands

class Destiny(commands.Cog):
    def __init__(self, client):
        self.client = client

    #TODO: Trouver un moyen plus élégant de remplacer la commande.
    @commands.command(aliases=['r', 'res'])
    async def resources(self, ctx, arg=None):
        """Returns a link to a folder of D2 resources"""
        if arg == 'lev':
            return await ctx.send('**Leviathan Resource Folder: https://drive.google.com/drive/folders/1W3FI2Ul17Z07XvGreYZySQhr84Wh6X5S?usp=sharing**')
        if arg == "lw":
            return await ctx.send('**Last Wish Resource Folder: https://drive.google.com/drive/folders/1YNIAlu1OJEH7NB4XDikS9UVwfuR_BJR6?usp=sharing.**')
        if arg == "sotp":
            return await ctx.send('**Scourge of the Past Resource Folder: https://drive.google.com/drive/folders/1yJZJrH2vwvERyLIFGfs-0JhpR9j88Vcp?usp=sharing.**')
        if arg == "cos":
            return await ctx.send('**Crown of Sorrows Resource Folder: https://drive.google.com/drive/folders/13PIjZW-EcmqbaeeQSFzhNeVLMyE9eixy?usp=sharing.**')
        if not arg:
            return await ctx.send("**Destiny 2 Resources Folder: https://drive.google.com/open?id=1HbTh5gHBKPH1EZC9bYi9HFQBGzJcHbfZ**")
        else:
            return await ctx.send(f"{arg} doesn't correspond to any of my registered arguments for this command, here's the **Destiny 2 Resources Foler:** https://drive.google.com/open?id=1HbTh5gHBKPH1EZC9bYi9HFQBGzJcHbfZ")
    
    @commands.command(aliases=['wpinfo'])
    async def weapon_info(self, ctx, *, nomArme: str):
        return

    async def cog_command_error(self, ctx, error):
        """Gère tous les exceptions non-attrapées."""
        return await Erreur.gestionnaire_erreur(ctx, error)