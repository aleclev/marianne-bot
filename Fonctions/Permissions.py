def _listerBits(n: int, longeur: int = 0) -> list:
    listeBits = [1 if digit=='1' else 0 for digit in bin(n)[2:]]
    if len(listeBits) > longeur:
        raise AttributeError
    else:
        listeBits = ((longeur - len(listeBits)) * [0]) + listeBits
        return listeBits

def _addSansRetenues(liste1: list, liste2: list) -> list:
    """Addition de deux liste de nombres sans retenues.
    La nouvel liste de nombres garde le
    max de chaque positions.

    Args:
        liste1 (list): Liste de nombres
        liste2 (list): Liste de nombres

    Raises:
        AttributeError: Les deux liste doivent avoir la même longueur.

    Returns:
        Liste(int): La liste des minimums de chaque position.
    """
    #Précondtion
    if len(liste1) != len(liste2):
        raise AttributeError
    else:
        #La liste qui sera retournée
        listeRet = liste1

        for n in range(0, len(listeRet)):
            listeRet[n] = max(liste1[n], liste2[n])
        
        return listeRet

def _sousSansRetenues(liste1: list, liste2: list) -> list:
    """Effectue l'opération inverse de addSansRetenues.
    liste1-liste2.

    Args:
        liste1 (list): [description]
        liste2 (list): [description]

    Raises:
        AttributeError: Les deux liste doivent avoir la même longueur.

    Returns:
        Liste(int): La liste des minimums de chaque position.
    """
    #Précondtion
    if len(liste1) != len(liste2):
        raise AttributeError
    else:
        #La liste qui sera retournée
        listeRet = liste1.copy()

        for n in range(0, len(listeRet)):
            listeRet[n] = 0 if liste1[n] == liste2[n] else 1
        
        return listeRet

def _reconstruireChampsBits(liste: list) -> int:
    """Retourne le nombre représenté par la liste de bits.

    Args:
        liste (int): Liste de bits.

    Returns:
        int: La valeur de la liste de bits.
    """
    listeStr = [str(n) for n in liste]
    bitsStr = "0b" + "".join(listeStr)
    return int(bitsStr, 2)

def additioner_permissions(valeurPerm1: int, valeurPerm2:int) -> int:
    """Permet de retourner la valeur de la permission qui représente l'union des permissions valeurPerm1 et valeurPerm2.
    Exemple: perm1 (AB), perm2 (BC) -> sortie (ABC).

    Args:
        valeurPerm1 (int): Valeur de la permission 1.
        valeurPerm2 (int): Valeur de la permission 2.

    Returns:
        int: Valeur de l'union des deux permissions.
    """
    liste1 = _listerBits(valeurPerm1, 64)
    liste2 = _listerBits(valeurPerm2, 64)
    listeRet = _addSansRetenues(liste1, liste2)

    return _reconstruireChampsBits(listeRet)

def soustraire_permissions(valeurPerm1: int, valeurPerm2:int) -> int:
    """Permet de retourner la valeur de la permission qui représente la soustraction des permissions valeurPerm1 et valeurPerm2.
    Exemple: perm1 (ABC), perm2 (BC) -> sortie (A).

    Args:
        valeurPerm1 (int): Valeur de la permission 1.
        valeurPerm2 (int): Valeur de la permission 2.

    Returns:
        int: Valeur de l'union des deux permissions.
    """
    liste1 = _listerBits(valeurPerm1, 64)
    liste2 = _listerBits(valeurPerm2, 64)
    listeRet = _sousSansRetenues(liste1, liste2)

    return _reconstruireChampsBits(listeRet)
    