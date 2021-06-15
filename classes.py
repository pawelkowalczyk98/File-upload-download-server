class Main:
    def __init__(self, typ, length, content):
        self.typ = typ
        self.length = length
        self.content = content
    # __________________________________________________________


class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __len__(self):
        return len(self.username) + len(self.password)


class Logout:
    def __init__(self, username):
        self.username = username

    def __len__(self):
        return len(self.username)


class Ls:
    def __init__(self, username, private, public):
        self.username = username
        self.private = private
        self.public = public

    # _______________________________________________
# > Może zawsze przy wysyłaniu klasy dodać do niej jakiegoś inta = 0,
# który będzie inkrementowany przy każdym wysłaniu klasy przez klienta o 1
# (zabezpieczenie przed podpięciem? Mati podawał taki przykład, mogę dodać)
# > No i może zmienić nazwy niektórym klasom? Teoretycznie przy rejestracji
# Mogłem użyć funkcji loguot, ale nazwa byłaby myląca, a robić drugiej
# identycznej klasy nie ma sensu