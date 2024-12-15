from .db import get_db

def register_user(email: str, security_key: str):
    db = get_db()
    users_collection = db["users"]
    if users_collection.find_one({"email": email}):
        return {"message": "El usuario ya está registrado."}
    users_collection.insert_one({"email": email, "security_key": security_key})
    return {"message": "Usuario registrado con éxito."}

def upload_file(file_name: str, file_data: bytes):
    db = get_db()
    files_collection = db["files"]
    files_collection.insert_one({"file_name": file_name, "file_data": file_data})
    return {"message": f"Archivo {file_name} cargado con éxito."}
