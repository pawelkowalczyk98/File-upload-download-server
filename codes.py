import pickle

dic_service_code = {
    # SUCCESSES
    101: "Successfully Logged in",
    102: "Successfully Logged out",
    103: "Username available",
    104: "Registration successful",

    # LOGIN/REGISTRATION ERRORS
    201: "Incorrect password",
    202: "Incorrect username",
    203: "Username unavailable",

    # FILE
    301: "Successfully. Start sending file. ",
    401: "File not exist."
}


# dic_service_code BACKUP
def codes_save():
    with open('dic_service_code.pkl', 'wb') as f:
        pickle.dump(dic_service_code, f)
        f.close()
