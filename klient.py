"""Client"""

# coding=utf-8
import socket
import pickle
import classes
import codes
import ssl

# __________________________________________________________
# GLOBAL VARIABLES
USER = ""
CRLF = b"\r\n\r\n"
# (Service action counter for safety - TO_DO)
SERVICE_CNT = 0

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='server.crt')
context.load_cert_chain(certfile='client.crt', keyfile='client.key')


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


# ____________________________________________________________
# Funkcje pomocnicze

def username_check(username, server):
    # Czy muszą to być klasy? Mati mówił, że to i tak te same rodzaje wiadomości :/
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


def receive_service_code(server):  # zwraca kod, jezeli service_code
    data = b''
    while b"\r\n\r\n" not in data:
        data += server.recv(1)
    data_obj = pickle.loads(data)  # ładowanie danych do struktur
    print(f'//I receive = {data_obj.typ} {data_obj.length} {data_obj.content}')  # wypisanie
    if data_obj.typ == "service_code":
        return data_obj.content


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(('localhost', 1769))
    with context.wrap_socket(sock, server_hostname='localhost') as s:
        print(s.version())
        print('WELCOME TO FTP-CLIENT!\n')

        while True:

            print('AVAILABLE COMMANDS: register, login, logout, help, exit\n')
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

            else:
                print("Incorrect command")

        s.close()

except socket.error:
    print('Error')
