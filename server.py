"""Server"""

# coding=utf-8
import socket
import pickle
import classes
import os
import ssl
from _thread import start_new_thread

# __________________________________________________________
# GLOBAL VARIABLES
CRLF = b"\r\n\r\n"
CODE_LEN = 3


set_user_login = set()  # loginy
dic_user_pwd = {}  # hasla
set_logged_in = set()  # set zalogowanych; mozna dodac generowanie
# rand liczby/portu ktora przypiszemy w mapie do usera dla bezpieczenstwa


def create_ssl_context():
    cont = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    cont.verify_mode = ssl.CERT_REQUIRED
    cont.load_cert_chain(certfile='server.crt', keyfile='server.key')
    cont.load_verify_locations(cafile='client.crt')
    return cont


def one_client(client):
    data = b''
    while b"\r\n\r\n" not in data:
        data += client.recv(1)
        # print(data)

    data_obj = pickle.loads(data)  # ładowanie danych do struktur
    print(f'I receive = {data_obj.typ} {data_obj.length}')  # wypisanie
    service_client(data_obj.typ, data_obj.content, client)
    client.close()


def add_user(username, password):
    set_user_login.add(username)
    dic_user_pwd[username] = password

    with open('set_user_login.txt', 'wb') as f:     # Zapis loginów
        pickle.dump(set_user_login, f)

    with open("dic_user_pwd.pkl", "wb") as f:       # Zapis haseł
        pickle.dump(dic_user_pwd, f)


# serwer za przy każdym uruchomieniu wczytuje loginy i hasła

with open('set_user_login.txt', 'rb') as f:         # odczyt loginów
    set_user_login = pickle.load(f)
print("Loginy:")
print(set_user_login)

with open("dic_user_pwd.pkl", "rb") as f:           # odczyt haseł
    dic_user_pwd = pickle.load(f)
print("Hasła:")
print(dic_user_pwd)


# ___________________________________________________________
# Uruchamianie odpowiednich funkcji

def service_client(function_type, content, client):
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

    if function_type == "download_file":
        print("\t download File")
        download_file(content.filename, content.typ, content.username, client)

    if function_type == "send_file":
        print("\t send File")
        send_file(content.filename, content.typ, content.username, content.ispublic, content.size, client)

    # _______________________________________________________


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

            set_logged_in.add(username)  # Dodanie do listy zalogowanych
            print("\t\tZalogowano: " + username)
            response_class = classes.Main("service_code", CODE_LEN, 101)
        else:
            print("\t\tBłędne hasło dla: " + username)
            response_class = classes.Main("service_code", CODE_LEN, 201)
    else:
        print("\t\tNieistniejący użytkownik: " + username)
        response_class = classes.Main("service_code", CODE_LEN, 202)

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

    # wysłać komunikat że ok
    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)


def username_check_service(username):
    print("\t\tTu odbywa się rejestracja użytkownika")
    if username in set_user_login:
        response_class = classes.Main("service_code", CODE_LEN, 203)
    else:
        # hasło potrzebne do rejstracji
        #add_user(username,password)
        response_class = classes.Main("service_code", CODE_LEN, 103)
    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)


def download_file(filename,typ,username,client):
    print("\t\t download file")
    path="server/"+filename
    # czy plik istnieje
    isExist = os.path.exists(path)
    if isExist == False:
        response_class = classes.Main("service_code",CODE_LEN, 401)
        response_object = pickle.dumps(response_class)
        client.sendall(response_object + CRLF)
        print("Plik nie istnieje")
        return
    # czy jest publiczy lub czy username jest właścielem
        # jeśli nie odpowieni kod błęd jeśli tak to wysyłanie:

    print("\t\tWysyłam plik")

    size = os.stat(path).st_size
    response_class = classes.Main("service_code", size, 301)
    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)
    # wyślij plik

    with open(path, 'rb') as f:
        data="a" # żeby data nie była pusta na początku
        while data:
            data = f.read(1)
            client.sendall((data))

    print("\t\tCorrect send")
    f.close()


def send_file(filename,typ,username,ispublic,size, client):
    print("\t\t zaraz bede zpisywał plik ")
    response_class = classes.Main("service_code", CODE_LEN , 301)
    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)
    data_size = 0
    path="server/"+filename
    with open(path, 'wb') as f:
        while data_size < size:
            data = client.recv(1)
            #print(data)
            data_size += 1
            f.write(data)
        f.close()
        print("zapisano")


# __________________________MAIN_LOOP____________________________
context = create_ssl_context()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind(("localhost", 1769))
    sock.listen(5)
    with context.wrap_socket(sock, server_side=True) as s:
        while True:
            try:
                client, address = s.accept()
                print("Connected: " + address[0])
                start_new_thread(one_client, (client,))

            except socket.error:
                s.close()

# ______________________________________
