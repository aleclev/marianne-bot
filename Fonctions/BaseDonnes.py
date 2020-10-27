import discord
import datetime
import pymysql
from Classes import MarianneException, GestionnaireResources
from discord.ext import commands, tasks

#TODO: Pourquoi est-ce que j'ai mis ça dans un cog??
class BaseDonnes(commands.Cog):
    def __init__(self, gestionnaireResources : GestionnaireResources.GestionnaireResources):
        self.reinit_bd_conn.start()
        self.connectionBD = gestionnaireResources.connectionBD

    @tasks.loop(seconds=1800)
    async def reinit_bd_conn(self):
        """Réinitialise la connexion mysql périodiquement (est supposé prévenir un erreur de timeout).
        """
        self.connectionBD.close()
        self.connectionBD.ping(reconnect=True)


