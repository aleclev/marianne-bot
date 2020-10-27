from Classes import AccesseurBD, VerificateurBD
from Fonctions import Erreur
import discord.ext.commands as commands
from praw import Reddit
import pymysql
import pydest
import discord
import requests

class GestionnaireResources():
    """Classe contenant l'ensemble des classes/variables
    qui devront être passés aux modules. Cette classe
    peut donc être passé seule dans le constructeur d'un 
    module.
    """
    def __init__(self, config : dict):
        #Dictionnaire dérivé du json
        self.config = config

        #Définition du client discord
        self.client = commands.Bot(command_prefix=config["prefix"], help_command=None)

        #Définition du client reddit
        self.reddit = Reddit(client_id=config["reddit_id_client"],
                            client_secret=config["redditClientSecret"],
                            password=config["redditMotPasse"],
                            user_agent=config["redditUtilisateurAgent"],
                            username=config["redditNomUtilisateur"])

        #Définition de la connection pymysql
        self.connectionBD = pymysql.connect(host=config["bd_nom_hote"],
                                user=config["bd_nom_utilisateur"],
                                password=config["bd_mot_passe"],
                                db=config["bd_nom"],
                                charset='utf8mb4',
                                autocommit=True,
                                cursorclass=pymysql.cursors.DictCursor)

        #Définition du client destiny
        self.clientDest = pydest.Pydest(api_key=config["cleDestiny"]) 

        #Définition d'une session pour faire des requêtes à l'api de bungie.
        self.sessionReq = requests.Session()

        #Définition du Vérificateur/Accesseur de la base de données
        self.verificateurBD = VerificateurBD.VerificateurBD(self.connectionBD)
        self.accesseurBD = AccesseurBD.AcesseurBD(self.connectionBD)
    
    def initModules(self, modulesVisibles : list = [], modulesCaches : list = []):
        """Permet d'initialiser une liste de modules. Les modules doivent être des classes qui héritent 
        de commands.Cog. LA CLASSE DOIT ÊTRE PASSÉE. Cette fonction utilise le constructeur. La liste de 
        modules visible sera visible au commandes de documentation. La liste de modules cachés ne le sera pas.

        Args:
            modulesVisibles (list, optional): La liste des modules visibles. Defaults to [].
            modulesCaches (list, optional): La liste des modules cachés. Defaults to [].
        """

        #TODO: Sous l'implémentation courante, le gestionnaire d'erreur global et local sont tous deux appelés.
        async def on_command_error(ctx, error):
            """Gestionnaire d'erreur générique. Redirige les erreurs des cogs visibles vers le gestionnaire d'erreur."""
            return await Erreur.gestionnaire_erreur(ctx, error)

        #Gestionnaire d'erreur global.
        self.client.on_command_error = on_command_error

        #Initialisation des modules visibles
        for module in modulesVisibles:
            nouvModule = module(self)
            module.cache = False     
            self.client.add_cog(module(self))

        #Initialisation des cogs non-visible.
        for module in modulesCaches:
            nouvModule = module(self)
            nouvModule.cache = True
            self.client.add_cog(nouvModule)