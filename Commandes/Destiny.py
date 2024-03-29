"""
Contient l'implémantation des commandes de Destiny.
"""

import discord
from Fonctions import Erreur
from Classes import GestionnaireResources
from Classes.GestionnaireResources import GestionnaireResources
from discord.ext import commands

class Destiny(commands.Cog):
    def __init__(self, gestionnaireResources : GestionnaireResources):
        self.client = gestionnaireResources.client
        self.gestRes = gestionnaireResources

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
    
    @commands.command()
    async def raid_compl(self, ctx: commands.Context):
        listeActiv = self.gestRes.accesseurBD.getTousActivInfo()
        id_bungie = await self.gestRes.accesseurBD.reqIDBungie(ctx.author)
        listeIDPerso = self.gestRes.accesseurBD.reqListeIDPersonnagesDest(id_bungie)
        listeDonneesPerso = await self.gestRes.accesseurBD.reqDonneesPersonnage(id_bungie, listeIDPerso)
        print(listeDonneesPerso)
        
        message = "```"

        for activ in listeActiv:
            listeHash = self.gestRes.accesseurBD.reqListeHashParIdRaid(activ["activ_id"])
            print(listeHash)
            compte = self.gestRes.accesseurBD.compterCompletions(listeDonneesPerso, listeHash)
            message += activ["activ_nom"] + " " + str(compte) + "\n"
        message += "```"

        return await ctx.send(message)
