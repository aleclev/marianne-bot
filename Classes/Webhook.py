import requests
import time
from pyngrok import ngrok
from flask import Flask, request, jsonify, Response

"""L'utilisateur initie avec une commande de Marianne.
    La commande apporte l'utilisateur sur http://aleclev.pythonanywhere.com/.
    L'utilisateur doit ensuite s'enregistrer sur steam à travers OpenID.
    Après un enregistrement, le site web retourne une requête JSON contenant un steamID et un Code d'authorization. Les deux sont sauvegardés dans listeCodesAuth.
    L'utilisateur utilise une autre commande de marianne pour comfirmer le code d'authorization sur discord.
    On peut alors trouver le code d'authorization spécifique dans la liste et l'associé au bon steamID. (On obtient le discordID depuis le contexte de la commande)
"""

class MarianneWebhook():
    def __init__(self):
        #Secret pour l'authentification des requêtes JSON.
        self.marianneSecret = "WvM2LIPPNegIBsR2Grmx"

        #Contient tous les codes d'authorizations pour chaque steamID enregistré. Format des données: [{"steamID": steamID, "CodeAuth": codeAuth, "Date": date}, ...]
        self.listeCodesAuth = []

        #URL Publique. Aucune autre modifications à faire.
        urlWebhook = ngrok.connect(port=8080)
        print(urlWebhook)

        #Site web public fréquenté par les utilisateurs.
        self.sitewebPublic = "https://aleclev.pythonanywhere.com"

        #Requête au serveur pour mettre à jour l'URL du webhook
        res = requests.post(f"{self.sitewebPublic}/majurl", json={"URL": urlWebhook, "MarianneAuth": self.marianneSecret})

        if res.ok:
            print("La requête de changement d'URL a été acceptée.")
        else:
            print("La requête de changement d'URL n'a pas été acceptée.")

        self.app = Flask(__name__)

        @self.app.route("/steamloginprocess", methods=["POST"])
        def steamIDListener():
            #Récupère les détails de la requête.
            content = request.json
            print(content)
            #Secret pour authetifier Marianne. Prévention de requêtes forgés.
            if content["MarianneAuth"] != self.marianneSecret:
                return Response(status=401)
            
            steamID = content["steamID"]
            codeAuth = content["CodeAuth"]
            print(f"Nouvelle requête: {steamID}, {codeAuth}")
            res = self.ajouterRequeteJSON(steamID, codeAuth, time.time())
            return Response(status=res)

    #Ajoute une nouvelle entrée dans listeCodeAuth en remplacant les duplicatas éventuels.
    def ajouterRequeteJSON(self, steamID: str, CodeAuth: str, date: float) -> int:
        """La fonction ajoute la requête à listeCodesAuth.

        Args:
            steamID (str): steamID envoyé avec la requête.
            CodeAuth (str): Code d'authentification de la requête.
            date (int): Temps UNIX de la requête.

        Returns:
            int: Code à retourner au site web.
        """
        for entree in self.listeCodesAuth:
            #Retour prématuré si le code d'authetification a un duplicata. (TRÈS peu probable)
            if entree["CodeAuth"] == CodeAuth:
                return 500
        for i in range(0, len(self.listeCodesAuth)):
            if self.listeCodesAuth[i]["steamID"] == steamID:
                self.listeCodesAuth[i] = {"steamID": steamID, "CodeAuth": CodeAuth, "Date": time.time()}
                return 200
            
        #Si le steamID n'est pas déjà dans la liste on l'ajoute simplement
        self.listeCodesAuth.append({"steamID": steamID, "CodeAuth": CodeAuth, "Date": time.time()})

    #TODO: Méthode pour enlever une entrée.
    def supprimerRequeteJSON(self, codeAuth: str):
        self.listeCodesAuth = [entree for entree in self.listeCodesAuth if entree["CodeAuth"] != codeAuth]
    
    def supprimerRequetesExpires(self):
        self.listeCodesAuth = [entree for entree in self.listeCodesAuth if time.time() - entree["Date"] < 600]
    
    def authetifierUtilisateur(self, codeAuth: str):
        """Retourne le steamID correspondant au code d'authentification. Si aucun code ne correspond ou le code est expiré, la fonction retroune None.

        Args:
            codeAuth (str): [description]

        Returns:
            str: Retourne le steamID correspondant au code d'authentification ou None si le code est invalide/expiré.
        """
        for entree in self.listeCodesAuth:
            #Le code doit être le bon et la requête ne doit pas être expirée.
            if entree["CodeAuth"] == codeAuth and time.time() - entree["Date"] < 600:
                return entree["steamID"]
        return None

        
    def activer(self):
        self.app.run(port=8080, debug=False)