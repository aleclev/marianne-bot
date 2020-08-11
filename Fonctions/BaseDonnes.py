import discord
import datetime
from discord.ext import commands, tasks

class BaseDonnes(commands.Cog):
    def __init__(self, connectionBD):
        self.reinit_bd_conn.start()
        self.connectionBD = connectionBD

    @tasks.loop(seconds=1800)
    async def reinit_bd_conn(self):
        """Réinitialise la connexion mysql périodiquement (est supposé prévenir un erreur de timeout).
        """
        self.connectionBD.close()
        self.connectionBD.ping(reconnect=True)
