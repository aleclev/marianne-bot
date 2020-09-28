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

class MauvaiseEntree(Exception):
    """Erreur associée à une entrée invalide."""
    def __init__(self):
        pass

class PermissionsDiscordManquante(Exception):
    def __init__(self, permission: str = 'Unspecified Permission'):
        self.permission = permission

class MarianneException(Exception):
    """"""
    def __init__(self):
        pass