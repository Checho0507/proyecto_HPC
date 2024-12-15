import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Eliminar todos los registros de la tabla 'usuarios'
cursor.execute("DELETE FROM users")

# Confirmar cambios
conn.commit()

print("Tabla 'usuarios' limpiada exitosamente.")

# Cerrar la conexión
conn.close()
