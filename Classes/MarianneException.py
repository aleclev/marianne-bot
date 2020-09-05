"""
Implémentation des exceptions de Marianne.
"""

class NonEnregSteam(Exception):
    """Erreur associée à un utilisateur sans steam_id enregistré dans la base de données."""
    def __init__(self):
        pass

class NonEnregDiscord(Exception):
    """Erreur associée à un utilisateur sans discord_id enregistré dans la base de données."""
    def __init__(self):
        pass

class MarianneException(Exception):
    """"""
    def __init__(self):
        pass