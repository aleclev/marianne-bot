"""
Fichier principal de Marianne. 
Marianne est une intégration pour Discord.
"""

from discord.ext import commands, tasks
import json
import pymysql
import requests
import pydest
from praw import Reddit
from Commandes import Util, Dev, Tag, Steam, Moderation, Marianne, Tag, Enregistrement, Destiny #Permet d'enlever une erreur avec le linting.
from Fonctions import BaseDonnes, Message

#TODO: Écrire un script pour transfèrer tous les données des tags enregistrés auparavant.
#TODO: Remplacer les notifs pour le formulaire d'application au clan.

def main():
    #Importation de config.json
    with open("config.json", "r") as f:
        config = json.loads(f.read())

    #Définition du client reddit
    reddit = Reddit(client_id=config["reddit_id_client"],
                        client_secret=config["redditClientSecret"],
                        password=config["redditMotPasse"],
                        user_agent=config["redditUtilisateurAgent"],
                        username=config["redditNomUtilisateur"])

    #Définition de la connection pymysql
    connection_BD = pymysql.connect(host=config["bd_nom_hote"],
                             user=config["bd_nom_utilisateur"],
                             password=config["bd_mot_passe"],
                             db=config["bd_nom"],
                             charset='utf8mb4',
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)
    
    #Définition d'une session pour faire des requêtes à l'api de bungie.
    sessionReq = requests.Session()

    #Définition du client destiny
    clientDest =pydest.Pydest(api_key=config["cleDestiny"])

    #Définition du client discord
    client = commands.Bot(command_prefix=config["prefix"], help_command=None)

    #Ajout des cogs du client
    #Cogs de commandes
    client.add_cog(Util.Util(client, config=config))
    client.add_cog(Dev.Dev(client, config=config, reddit=reddit, clientDest=clientDest, connectionBD=connection_BD))
    client.add_cog(Moderation.Moderation(client))
    client.add_cog(Marianne.Marianne(client))
    client.add_cog(Tag.Tag(client, connectionBD=connection_BD))
    client.add_cog(Enregistrement.Enregistrement(client, connectionBD=connection_BD, config=config))
    client.add_cog(Steam.Steam(client, config=config, connectionBD=connection_BD, sessionReq=sessionReq, clientDest=clientDest))
    client.add_cog(Destiny.Destiny(client))

    #Marque tous les engrenages de cette section comme non cachés. (Utile dans les commandes de documentations)
    listeEngr = client.cogs
    for cogNom in listeEngr:
        listeEngr[cogNom].cache = False
    
    #Cogs de Fonctions
    client.add_cog(BaseDonnes.BaseDonnes(connectionBD=connection_BD))
    client.add_cog(Message.MessagesFonctions(client=client))

    #Marque tous les engrenages de cette section comme cachés. (Utile dans les commandes de documentations)
    listeEngr = client.cogs
    for cogNom in listeEngr:
        if not hasattr(listeEngr[cogNom], "cache"): 
            listeEngr[cogNom].cache = True

    #Confirmation du bot en console.
    @client.event
    async def on_ready():
        print(f"{config['nom']} est en ligne!")

    #Éxcecute le client discord
    client.run(config["jetton"])

    return 0

if __name__ == "__main__":
    main()