import requests

BASE_URL = "http://127.0.0.1:8000"

def seed_administrador():
    admin = {
        "nombre": "admin",
        "correo": "admin@outlook.com",
        "contraseña": "123456789"  # Se hasheará automáticamente en el backend
    }
    
    response = requests.post(f"{BASE_URL}/administrador/", json=admin)
    if response.status_code == 201:
        print(f"✅ Administrador creado: {admin['nombre']} - {admin['correo']}")
        print(f"   ID: {response.json()['id_administrador']}")
        print(f"   ⚠️  Contraseña temporal: {admin['contraseña']}")
    else:
        print(f"❌ Error al crear administrador: {response.status_code}")
        print(f"   Respuesta: {response.text}")

if __name__ == "__main__":
    print("🔐 Creando administrador...\n")
    seed_administrador()
