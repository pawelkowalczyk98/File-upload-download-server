import pickle

dic_service_code = {101: "Successfully Logged in",
                    102: "Successfully Logged out",
                    103: "Username available",
                    201: "Incorrect password",
                    202: "Incorrect username",
                    203: "Username unavailable"}


# dic_service_code BACKUP
def codes_save():
    with open('dic_service_code.pkl', 'wb') as f:
        pickle.dump(dic_service_code, f)
        f.close()
