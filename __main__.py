"""
Fichier principal de Marianne. 
Marianne est une intégration pour Discord.
"""

import discord
from discord.ext import commands, tasks
import json
import pymysql
import requests
import pydest
from praw import Reddit
from Commandes import Util, Dev, Tag, Steam, Moderation, Marianne, Tag, Enregistrement, Destiny, Role, NotificationsTag #Permet d'enlever une erreur avec le linting.
from Commandes.SherpaRun import Clan
from Commandes.SherpaRun import Role as RoleSR
from Classes import GestionnaireResources
from Fonctions import BaseDonnes, Message, Erreur

def main() -> int:
    #Importation de config.json
    with open("config.json", "r") as f:
        config = json.loads(f.read())
    
    #Gestionnaire de resources
    gestRes = GestionnaireResources.GestionnaireResources(config)

    #Liste des classes de modules/cogs cachés et visible. La visibilité influence la commande de documentation.
    modulesVisibles = [
        Util.Util,
        Moderation.Moderation,
        Marianne.Marianne,
        Tag.Tag,
        Enregistrement.Enregistrement,
        Steam.Steam,
        Destiny.Destiny,
        Role.Role,
        Clan.Clan,
        NotificationsTag.NotificationsTag#,
        #RoleSR.Role
    ]

    modulesCaches = [
        Dev.Dev,
        BaseDonnes.BaseDonnes,
        Message.MessagesFonctions
    ]

    gestRes.initModules(modulesVisibles, modulesCaches, True)

    #Éxcecute le client discord
    gestRes.client.run(config["jetton"])

    return 0

if __name__ == "__main__":
    main()
