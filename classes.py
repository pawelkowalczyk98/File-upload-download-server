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
    def __init__(self, username, sid):
        self.username = username
        self.sid = str(sid)

    def __len__(self):
        return len(self.username) + len(self.sid)


class Register:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __len__(self):
        return len(self.username) + len(self.password)


class Ls:
    def __init__(self, username, own, public,files_list):
        self.username = username
        self.own = own
        self.public = public
        self.files_list = files_list

class Download_file:
    def __init__(self, filename, typ, username):
        self.filename = filename
        self.typ = typ
        self.username = username


class Send_file:
    def __init__(self, filename, typ, username, ispublic, size):
        self.filename = filename
        self.typ = typ
        self.username = username
        self.ispublic = ispublic
        self.size = size


# _______________________________________________
# > Może zawsze przy wysyłaniu klasy dodać do niej jakiegoś inta = 0,
# który będzie inkrementowany przy każdym wysłaniu klasy przez klienta o 1
# (zabezpieczenie przed podpięciem? Mati podawał taki przykład, mogę dodać)
# > No i może zmienić nazwy niektórym klasom? Teoretycznie przy rejestracji
# Mogłem użyć funkcji loguot, ale nazwa byłaby myląca, a robić drugiej
# identycznej klasy nie ma sensu