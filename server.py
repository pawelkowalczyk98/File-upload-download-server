"""Server"""

# coding=utf-8
import socket
import pickle
import classes

# __________________________________________________________
# GLOBAL VARIABLES
CRLF = b"\r\n\r\n"
CODE_LEN = 3

# Definicje klas protokołu

set_user_login = set()  # loginy
dic_user_pwd = {}  # hasla
set_logged_in = set()  # set zalogowanych; mozna dodac generowanie
# rand liczby/portu ktora przypiszemy w mapie do usera dla bezpieczenstwa


## Zapisywanie seta z loginami:
# with open('set_user_login.txt', 'wb') as f:
#    pickle.dump(set_user_login, f)
## Odczytywanie seta:
# with open('set_user_login.txt', 'rb') as f:
#    user_data = pickle.load(f)
## Zapisywanie dict z haslami:
# with open("data.pkl", "wb") as f:
#    pickle.dump(dic_user_pwd, f)
## Odczytywanie dict:
# with open("data.pkl", "rb") as f:
#    dic_user_pwd = pickle.load(f)

## Dodanie konta root z haslem toor
set_user_login.add("root")
dic_user_pwd["root"] = "toor"


# ___________________________________________________________
# Uruchamianie odpowiednich funkcji

def service_client(function_type, content):
    """Funkcja na podstawie typu
    odpala odpowiednią funkcję"""

    if function_type == "login":
        print("\tlogin")
        login_service(content.username, content.password)

    if function_type == 'logout':
        print("\tlogout")
        logout_service(content.username)

    if function_type == 'username_check':
        print("\tusername checking..")
        username_check_service(content)
    # _______________________________________________________


# fnkcje serwera

""" 
TU zdefiniowane są funkcionalności serwera 
"""


# Obsługa logowania
def login_service(username, password):
    print("\t\tTu odbywa się logowanie do serwera")
    print("\t\tUsername: " + username)
    print("\t\tPassword: " + password)

    # Czy login istnieje?
    if username in set_user_login:
        # Czy hasło poprawne?
        if password == dic_user_pwd[username]:
            # Czy już zalogowany?
            if username in set_logged_in:
                print("\t\tPrzelogowanie: " + username)
                # Wyloguj starego i zaloguj nowego? Nowy port?
            else:
                set_logged_in.add(username)  # Dodanie do listy zalogowanych
                print("\t\tZalogowano: " + username)
                response_class = classes.Main("service_code", CODE_LEN, 101)
        else:
            print("\t\tBłędne hasło dla: " + username)
            response_class = classes.Main("service_code", CODE_LEN, 201)
    else:
        print("\t\tNieistniejący użytkownik: " + username)
        response_class = classes.Main("service_code", CODE_LEN, 202)

    # Oznaczyć że username został zalogowany.
    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)


def logout_service(username):
    print("\t\tTu odbywa się wylogowywanie z serwera")
    print("\t\tUsername: " + username)
    if username in set_logged_in:
        set_logged_in.remove(username)
        print("\t\tWylogowano: " + username)
        response_class = classes.Main("service_code", CODE_LEN, 102)
        # Dodać jakieś rozłączenie klienta? np. if 102 then cośtam

    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)
    # wysłać komunikat że ok, albo że się nie powiodło


def username_check_service(username):
    print("\t\tTu odbywa się rejestracja użytkownika")
    if username in set_user_login:
        response_class = classes.Main("service_code", CODE_LEN, 203)
    else:
        response_class = classes.Main("service_code", CODE_LEN, 103)

    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)


# __________________________MAIN_LOOP____________________________
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("localhost", 1769))
s.listen(5)

while True:
    client, addr = s.accept()
    print("Connected: " + addr[0])
    while True:
        # Tą pętle trzeba wsadzić do funkcji i odpalać asyncio
        # odbieranie danych
        data = b''
        while b"\r\n\r\n" not in data:
            data += client.recv(1)
            # print(data)

        data_obj = pickle.loads(data)  # ładowanie danych do struktur
        print(f'I receive = {data_obj.typ} {data_obj.length}')  # wypisanie

        service_client(data_obj.typ, data_obj.content)

    client.close()

s.close()

# ______________________________________
