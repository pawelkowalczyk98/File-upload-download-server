"""Server"""

# coding=utf-8
import socket
import pickle
import classes
import os
import ssl
import random
from _thread import start_new_thread
import datetime

# __________________________________________________________

# GLOBAL VARIABLES
CRLF = b"\r\n\r\n"
CODE_LEN = 3

set_user_login = set()  # loginy
dic_user_pwd = {}  # hasla
set_logged_in = set()  # set zalogowanych; mozna dodac generowanie
dic_user_session = {
    # (session_id == 0) ==> public user, no account
    0: "public"
}
dic_session_user = {
    "public": 0
}
dic_file_owner = {}
dic_file_isPublic = {}


def log(content):
    time = datetime.datetime.now()
    with open("log/log.txt", "a") as f:
        f.write(str(time) +"\t" + str(content) + "\n")


def create_ssl_context():
    cont = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    cont.verify_mode = ssl.CERT_REQUIRED
    cont.load_cert_chain(certfile='server.crt', keyfile='server.key')
    cont.load_verify_locations(cafile='client.crt')
    log("create ssl contex")
    return cont


def one_client(cl, address):
    while True:
        data = b''
        while b"\r\n\r\n" not in data:
            data += cl.recv(1)
            # print(data)

        data_obj = pickle.loads(data)  # ładowanie danych do struktur
        print(f'I receive = {data_obj.typ} {data_obj.length}')  # wypisanie
        log_str = "\tI receive = " + str(data_obj.typ) +"\tlen: " + str(data_obj.length)
        log( str(address) + log_str)
        if data_obj.typ == "exit":
            print("Client disconnected from server.")
            cl.close()
            log(str(address) + "close connection")
            break
        service_client(data_obj.typ, data_obj.content, cl, address)


def save_dic(): # zapisuje globalne słowniki do plików
    with open('set_user_login.txt', 'wb') as f:  # Zapis loginów
        pickle.dump(set_user_login, f)

    with open("dic_user_pwd.pkl", "wb") as f:  # Zapis haseł
        pickle.dump(dic_user_pwd, f)

    with open('dic_file_owner.txt', 'wb') as f:  # Zapis właścicieli
        pickle.dump(dic_file_owner, f)

    with open('dic_file_isPublic.txt', 'wb') as f:  # Zapis flag dostępu
        pickle.dump(dic_file_isPublic, f)

    log("Save directory to file")


def add_user(username, password):
    set_user_login.add(username)
    dic_user_pwd[username] = password
    log("Add user \t username: " + username + "password: " + password)
    save_dic()


# serwer za przy każdym uruchomieniu wczytuje loginy i hasła
def read_dic():
    global set_user_login
    global dic_user_pwd
    global dic_file_owner
    global dic_file_isPublic

    with open('set_user_login.txt', 'rb') as f:  # odczyt loginów
        set_user_login = pickle.load(f)
    print("Loginy:")
    print(set_user_login)

    with open("dic_user_pwd.pkl", "rb") as f:  # odczyt haseł
        dic_user_pwd = pickle.load(f)
    print("Hasła:")
    print(dic_user_pwd)
    log("Read login and pass from file")

    # serwer za przy każdym uruchomieniu wczytuje słowniki
    with open('dic_file_owner.txt', 'rb') as f:  # odczyt plik-właściciel
        dic_file_owner = pickle.load(f)

    print("plik : własciciel ")
    print(dic_file_owner)

    with open("dic_file_isPublic.txt", "rb") as f:  # odczyt flagi pliku
        dic_file_isPublic = pickle.load(f)
    print("Flagi plików:")
    print(dic_file_isPublic)
    log("Read dictionary from file")


# ___________________________________________________________
# Uruchamianie odpowiednich funkcji
def service_client(function_type, content, client, address):
    """Funkcja na podstawie typu
    odpala odpowiednią funkcję"""

    if function_type == "login":
        print("\tlogin")
        login_service(content.username, content.password, address)

    if function_type == 'logout':
        print("\tlogout")
        logout_service(content.username, content.sid, address)

    if function_type == 'username_check':
        print("\tusername checking..")
        username_check_service(content, address)

    if function_type == "register":
        user_registration_service(content.username, content.password, address)

    if function_type == "download_file":
        print("\t download File")
        download_file(content.filename, content.typ, content.username, client, address)

    if function_type == "send_file":
        print("\t send File")
        send_file(content.filename, content.typ, content.username, content.ispublic, content.size, client, address)

    if function_type == "ls":
        print("\t ls")
        ls_files(content.username, content.own, content.public, client, address)
    # _______________________________________________________


""" 
TU zdefiniowane są funkcionalności serwera 
"""


# Obsługa logowania
def login_service(username, password, address):
    print("\t\tTu odbywa się logowanie do serwera")
    print("\t\tUsername: " + username)
    print("\t\tPassword: " + password)
    log(str(address) + "\tTry login. \tUsername: " + username + " password: " + password)
    # Czy login istnieje?
    if username == 'public':
        print("\t\tNie można zalogować na konto 'public'!")
        response_class = classes.Main("service_code", CODE_LEN, 202)
        log(str(address) + "\tCannot login on 'public' user.")
    elif username in set_user_login:
        # Czy hasło poprawne?
        if password == dic_user_pwd[username]:
            if username in set_logged_in:
                print("\t\tJuż zalogowany: " + username)
                response_class = classes.Main("service_code", CODE_LEN, 101)
                response_object = pickle.dumps(response_class)
                client.sendall(response_object + CRLF)
                response_class = dic_session_user[username]
                log(str(address) + "\tLogin sucesfull. \tSession_id: " + str(dic_session_user[username]))
            else:
                set_logged_in.add(username)  # Dodanie do listy zalogowanych
                session_id = random.randint(1, 999999)
                while session_id in dic_user_session:
                    session_id = random.randint(1, 999999)
                dic_user_session[session_id] = username
                dic_session_user[username] = session_id
                print("\t\tZalogowano: " + username)
                response_class = classes.Main("service_code", CODE_LEN, 101)
                response_object = pickle.dumps(response_class)
                client.sendall(response_object + CRLF)
                response_class = session_id
                log(str(address) + "\tLogin sucesfull. \tSession_id: " + str(session_id))
        else:
            print("\t\tBłędne hasło dla: " + username)
            response_class = classes.Main("service_code", CODE_LEN, 201)
            log(str(address) + "\tBad password")
    else:
        print("\t\tNieistniejący użytkownik: " + username)
        response_class = classes.Main("service_code", CODE_LEN, 202)
        log(str(address) + "\tInvalid Username")
    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)


def logout_service(username, sid, address):
    print("\t\tTu odbywa się wylogowywanie z serwera")
    print("\t\tUsername: " + username)
    sid = int(sid)
    log(str(address) + "\tLogout \tUsername: " + username + " session_id: " +str(sid))
    if username in set_logged_in:
        if dic_user_session[sid] == username:
            set_logged_in.remove(username)
            dic_user_session.pop(sid)
            dic_session_user.pop(username)

            print("\t\tWylogowano: " + username)
            response_class = classes.Main("service_code", CODE_LEN, 102)
            log(str(address) + "\tLogout complete. \tUsername: " + username)

            # Dodać jakieś rozłączenie klienta? np. if 102 then cośtam| NOM
        else:
            response_class = classes.Main("service_code", CODE_LEN, 204)
    else:
        response_class = classes.Main("service_code", CODE_LEN, 205)

    # wysłać komunikat że ok
    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)


def username_check_service(username,address):
    print("\t\tTu odbywa się rejestracja użytkownika")
    log(str(address) + "\tCheck available username: " + username )
    if username in set_user_login:
        response_class = classes.Main("service_code", CODE_LEN, 203)
        log(str(address) + "\tUsername: " + username + " is not available.")
    else:
        response_class = classes.Main("service_code", CODE_LEN, 103)
        log(str(address) + "\tUsername: " + username + " is available.")

    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)


def user_registration_service(username, password, address):
    set_user_login.add(username)
    dic_user_pwd[username] = password
    response_class = classes.Main("service_code", CODE_LEN, 104)
    client.sendall(pickle.dumps(response_class) + CRLF)
    save_dic()
    log(str(address) + "\tUser registration. \tusername: " + username + " password" + password)


def download_file(filename, typ, username, client, address):
    print("\t\t download file")
    log(str(address) + "\tUser try download file. \tusername: " + username + " filename: " + filename )
    path = "server/" + filename
    # czy plik istnieje
    isExist = os.path.exists(path)
    if isExist == False:
        response_class = classes.Main("service_code", CODE_LEN, 401)
        response_object = pickle.dumps(response_class)
        client.sendall(response_object + CRLF)
        print("Plik nie istnieje")
        log(str(address) + "\tFile not exist. \tusername: " + username + " filename: " + filename)
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
        data = "a"  # żeby data nie była pusta na początku
        while data:
            data = f.read(1)
            client.sendall(data)

    print("\t\tCorrect send")
    f.close()
    log(str(address) + "\tFile send correctly \tusername: " + username + " filename: " + filename)


def send_file(filename, typ, username, ispublic, size, client, address):
    print("\t\t zaraz bede zpisywał plik ")
    log(str(address) + "\tUser try send file \tusername: " + username + " filename: " + filename + " ispublic: " + ispublic)
    response_class = classes.Main("service_code", CODE_LEN, 301)
    response_object = pickle.dumps(response_class)
    client.sendall(response_object + CRLF)
    data_size = 0
    path = "server/" + filename
    # Tworzy odpowiedni katalog użytkownika (sprawdzić czy tylko u mnie na linuxie nie działa):
    # path = "/server/" + username + "/" + filename
    # os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'wb') as f:
        while data_size < size:
            data = client.recv(1)
            # print(data)
            data_size += 1
            f.write(data)
        f.close()
    dic_file_owner[filename] = username
    dic_file_isPublic[filename] = ispublic
    save_dic()
    print("zapisano")
    log(str(address) + "\tSaved file correctly \tusername: " + username + " filename: " + filename + " ispublic: " + ispublic)


def ls_files(username, own, public, client, address):
    print("\t\t ls files ")
    log(str(address) + "\tUser ls file. \t username: " + username + " owner file: " + str(own) + " public file: " + str(public))
    if username in set_logged_in: # jeśli zalogowany
        response_class = classes.Main("service_code", CODE_LEN, 100)
        response_object = pickle.dumps(response_class)
        client.sendall(response_object + CRLF)
        result_list = []

        if own:
            result_list = []
            for file in dic_file_owner:
                if dic_file_owner[file] == username:
                    result_list.append(file)

            response = classes.Ls(username,own,public,result_list)
            response_class = classes.Main("ls", len(result_list), response)
            response_object = pickle.dumps(response_class)
            client.sendall(response_object + CRLF)
            log(str(address) + "\tServer sent list of the owner files. \t username: " + username + " owner file: " + str(own) +  " public file: " + str(public))

        if public:
            result_list = []
            for file in dic_file_isPublic:
                if dic_file_isPublic[file]:
                    result_list.append(file)

            response = classes.Ls(username, own, public, result_list)
            response_class = classes.Main("ls", len(result_list), response)
            response_object = pickle.dumps(response_class)
            client.sendall(response_object + CRLF)
            log(str(address) + "\tServer sent list of the public files. \t username: " + username + " owner file: " + str(own) + " public file: " + str(public))

    else:
        response_class = classes.Main("service_code", CODE_LEN, 205)
        response_object = pickle.dumps(response_class)
        client.sendall(response_object + CRLF)
        log(str(address) + "\tUser not logged in, \t username: " + username + " owner file: " + str(own) + " public file: " + str(public))


# __________________________MAIN_LOOP____________________________
log("Start server")
read_dic()
context = create_ssl_context()
# Raczej źle, bo działa tylko na ipv6
if socket.has_dualstack_ipv6():
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0) as sock:
        sock.bind(("localhost", 1769))
        sock.listen(5)
        with context.wrap_socket(sock, server_side=True) as s:
            while True:
                try:
                    client, address = s.accept()
                    print("Connected: " + address[0])
                    log(str(address[0]) + " Connected" )
                    start_new_thread(one_client, (client, address[0],))

                except socket.error:
                    s.close()
else:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind(("localhost", 1769))
        sock.listen(5)
        with context.wrap_socket(sock, server_side=True) as s:
            while True:
                try:
                    client, address = s.accept()
                    print("Connected: " + address[0])
                    log(str(address[0]) + " Connected")
                    start_new_thread(one_client, (client, address[0],))

                except socket.error:
                    s.close()
# ______________________________________
