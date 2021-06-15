"""Client"""

# coding=utf-8
import socket
import pickle
import classes
import codes
import os
# __________________________________________________________
# GLOBAL VARIABLES
USER = ""
CRLF = b"\r\n\r\n"
# (Service action counter for safety - TO_DO)
SERVICE_CNT = 0


# __________________________________________________________
# PROTOCOL FUNCTIONS
#   Funkcje klienta
def login_service(server):
    global USER
    USER = input("Username: ")
    password = input("Password: ")
    data_login = classes.Login(USER, password)
    data = classes.Main("login", len(data_login), data_login)
    data_string = pickle.dumps(data)
    s.sendall(data_string + CRLF)
    receive(server)


def logout_service(server):
    data_logout = classes.Logout(USER)
    data = classes.Main("logout", len(data_logout), data_logout)
    data_string = pickle.dumps(data)
    s.sendall(data_string + CRLF)
    receive(server)


def register_service(server):
    global USER
    USER = input("Please enter desired username (or leave empty to cancel operation): ")
    # Must check if user contains only a-z and A-Z chars!
    if USER == '':
        print("Operation cancelled.")
    else:
        code = username_check(USER, server)
        if code == 103:
            print(codes.dic_service_code[code])
            # create user
        elif code == 203:
            print(codes.dic_service_code[code] + "\nTry again? (y/n)")
            if input("> ") == 'y':
                register_service(server)

def download_services(server): # poprawić size
    global USER
    filename= input("Filename: ")
    typ = input("Typ: ")
    data_download = classes.Download_file(filename,typ,USER)
    data = classes.Main("download_file", 5, data_download)
    data_string = pickle.dumps(data)
    s.sendall(data_string + CRLF)
    data_obj = receive(server)
    if data_obj.typ == "service_code":
        if data_obj.content == 301:
            # plik będzie leciał normalnie bez żadnej ramki. to będzie 2 typ wiadmości
            size = int(data_obj.length)
            data_size = 0
            with open(filename, 'wb') as f:
                while data_size < size:
                    data = server.recv(1)
                    #print(data)
                    data_size += 1
                    f.write(data)
                f.close()
                print("zapisano")


def send_services(server):
    global USER
    print("SEND FILES")
    filename = input("Filename: ")
    typ = input("Typ: ")

    isExist = os.path.exists(filename)
    if isExist == False:
        print("File not found")
        return

    x = input("Do you want your file to be public ? [yes/no]")
    if x == "yes":
        ispublic = True
    else:
        ispublic = False

    size = os.stat(filename).st_size

    data_send = classes.Send_file(filename, typ, USER, ispublic, size)
    data = classes.Main("send_file", 3, data_send)
    data_string = pickle.dumps(data)
    s.sendall(data_string + CRLF)
    data_obj = receive(server)

    if data_obj.typ == "service_code":
        if data_obj.content == 301:
            with open(filename, 'rb') as f:
                data = "a"  # żeby data nie była pusta na początku
                while data:
                    data = f.read(1)
                    server.sendall((data))

            print("\t\tCorrect send")
            f.close()
# ____________________________________________________________
# Funkcje pomocnicze

def username_check(username, server): # hasło jeszce
    # Czy muszą to być klasy? Mati mówił, że to i tak te same rodzaje wiadomości :/
    # nie mam pojęcia tak wydawało mi się że tak będzie najprościej
    data = classes.Main("username_check", len(username), username)
    data_string = pickle.dumps(data)
    s.sendall(data_string + CRLF)
    return receive_service_code(server)


def service_server(function_type, content):
    if function_type == "service_code":
        print(codes.dic_service_code[content])
        # inne wiadomości jakie server może wysłać do klienta


def receive(server):  # odbiera od servera wiadomości i przekazuje do service_server
    data = b''
    while b"\r\n\r\n" not in data:
        data += server.recv(1)
    data_obj = pickle.loads(data)  # ładowanie danych do struktur
    print(f'//I receive = {data_obj.typ} {data_obj.length} {data_obj.content}')  # wypisanie
    service_server(data_obj.typ, data_obj.content)
    return data_obj


def receive_service_code(server):  # zwraca kod, jezeli service_code
    data = b''
    while b"\r\n\r\n" not in data:
        data += server.recv(1)
    data_obj = pickle.loads(data)  # ładowanie danych do struktur
    print(f'//I receive = {data_obj.typ} {data_obj.length} {data_obj.content}')  # wypisanie
    if data_obj.typ == "service_code":
        return data_obj.content


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('localhost', 1769))

    while True:
        cmd = input('> ')

        if cmd == 'exit':
            break

        elif cmd == 'help':
            print('*Insert function description here*')

        elif cmd == 'login':
            login_service(s)

        elif cmd == 'logout':
            logout_service(s)

        elif cmd == 'register':
            register_service(s)

        elif cmd == 'download':
            download_services(s)

        elif cmd == 'send':
            send_services(s)

        else:
            print("Incorrect command")

except socket.error:
    print('Error')
