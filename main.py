from google.cloud import secretmanager
import dns.resolver
import requests
import json
import urllib3
import os

urllib3.disable_warnings()

# Configuraciones de Fortinet
FORTINET_BASE_URL = os.getenv('FORTINET_BASE_URL', "https://fortigate.gustavoortega.com.ar/api/v2/")
GROUP_NAME = os.getenv('GROUP_NAME', "CloudFlare IPv4 List")  # Valor predeterminado si la variable de entorno no está definida
PREFIX_NAME_OBJ = os.getenv('PREFIX_NAME_OBJ', "CloudFlare")
VERIFY_SSL = False
GCP_PROJECT = os.getenv('GCP_PROJECT', "fortinet-scripts")
SOURCE = os.getenv('SOURCE', { "type": "url_response", "hostname": "https://www.cloudflare.com/ips-v4/#"})
SECRET_NAME_APIKEY = os.getenv('SECRET_NAME_APIKEY', "prod_fortinet_apikey-manage-address")


# Función para obtener la API Key desde GCP Secret Manager
def obtener_api_key(GCP_PROJECT, SECRET_NAME_APIKEY):
    """
    Retorna el valor del secreto especificado desde GCP Secret Manager.

    Args:
    nombre_proyecto: ID del proyecto de GCP.
    nombre_secreto: Nombre del secreto en Secret Manager.

    Returns:
    Valor del secreto como una cadena de texto.
    """
    client = secretmanager.SecretManagerServiceClient()
    nombre = f"projects/{GCP_PROJECT}/secrets/{SECRET_NAME_APIKEY}/versions/latest"
    response = client.access_secret_version(name=nombre)
    return response.payload.data.decode('UTF-8')

API_KEY = obtener_api_key(GCP_PROJECT, SECRET_NAME_APIKEY)

# Headers para las solicitudes a la API de FortiGate
HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

def obtener_ips_dns(dominio):
    """Realiza un query DNS y retorna una lista de IPs."""
    try:
        answers = dns.resolver.resolve(dominio, 'A')
        return [rdata.to_text() for rdata in answers]
    except Exception as e:
        print(f"Error al realizar el query DNS: {e}")
        return []
    
def obtener_ips_de_url(url):
    """Consulta una URL y extrae una lista de IPs del contenido del body, asumiendo que cada IP está en su propia línea."""
    try:
        # Realiza la solicitud HTTP a la URL proporcionada
        respuesta = requests.get(url)
        respuesta.raise_for_status()  # Asegura que la solicitud fue exitosa

        # Separa el contenido del body por líneas y devuelve la lista
        ips = respuesta.text.splitlines()
        return ips
    except requests.RequestException as e:
        print(f"Error al realizar la solicitud HTTP: {e}")
        return []
    except Exception as e:
        print(f"Error al procesar las IPs: {e}")
        return []

def obtener_address_objects():
    """Obtiene los objetos de dirección actuales en FortiGate."""
    url = FORTINET_BASE_URL + f"cmdb/firewall/address?format=name|subnet&filter=name=@{PREFIX_NAME_OBJ}"
    try:
        VERIFY_SSL = False
        response = requests.get(url, headers=HEADERS, verify=VERIFY_SSL)
        response.raise_for_status()
        return response.json()["results"]
    except Exception as e:
        print(f"Error al obtener objetos de dirección: {e}")
        return []

def crear_o_actualizar_address_object(ip, address_objects):
    """Crea o actualiza un objeto de dirección para la IP dada si no existe."""
    objeto_nombre = f"{PREFIX_NAME_OBJ}_{ip}"
    print(objeto_nombre)
    # Comprueba si el objeto ya existe
    objeto_existente = next((obj for obj in address_objects if obj['name'] == objeto_nombre), None)

    url = FORTINET_BASE_URL + "cmdb/firewall/address/"
    if "/" in ip:
        ip,subnet = ip.split("/")
        data = {
            "name": objeto_nombre,
            "type": "ipmask",
            "subnet": f"{ip}/{subnet}"
        }
    else:
        data = {
            "name": objeto_nombre,
            "type": "ipmask",
            "subnet": f"{ip}/32"
        }

    if objeto_existente:
        # Actualiza el objeto existente si ya existe
        url += objeto_nombre
        try:
            response = requests.put(url, headers=HEADERS, json=data, verify=VERIFY_SSL)
            response.raise_for_status()
            print(f"Objeto de dirección actualizado: {objeto_nombre}")
        except Exception as e:
            print(f"Error al actualizar el objeto de dirección {objeto_nombre}: {e}")
    else:
        # Crea un nuevo objeto si no existe
        try:

            response = requests.post(url, headers=HEADERS, json=data, verify=VERIFY_SSL)
            response.raise_for_status()
            print(f"Objeto de dirección creado: {objeto_nombre}")
        except Exception as e:
            print(f"Error al crear el objeto de dirección {objeto_nombre}: {e}")


def actualizar_grupo_address(ips_dns, address_objects):
    """Actualiza el grupo de direcciones con las nuevas IPs, quitando las obsoletas y eliminándolas si es necesario."""
    nombres_nuevos = [f"{PREFIX_NAME_OBJ}_{ip}" for ip in ips_dns]
    nombres_a_eliminar = []

    # Encuentra el grupo por su nombre
    url_grupo = FORTINET_BASE_URL + f"cmdb/firewall/addrgrp/{GROUP_NAME}"
    try:
        response_grupo = requests.get(url_grupo, headers=HEADERS, verify=VERIFY_SSL)
        response_grupo.raise_for_status()
        
        miembros_actuales = [miembro["name"] for miembro in response_grupo.json()["results"][0]["member"]]
        nombres_a_eliminar = [nombre for nombre in miembros_actuales if nombre not in nombres_nuevos]
        
        # Prepara la lista de miembros actualizada
        miembros_actualizados = [{"name": nombre} for nombre in nombres_nuevos]

        # Actualiza el grupo de direcciones
        data = {"member": miembros_actualizados}
        response_actualizacion = requests.put(url_grupo, headers=HEADERS, json=data, verify=VERIFY_SSL)
        response_actualizacion.raise_for_status()
        print("Grupo de direcciones actualizado con éxito.")
        
        # Elimina los objetos de dirección obsoletos
        for nombre in nombres_a_eliminar:
            eliminar_objeto_address(nombre)

    except Exception as e:
        print(f"Error al actualizar el grupo de direcciones: {e}")

def eliminar_objeto_address(nombre_objeto):
    """Elimina un objeto de dirección en FortiGate."""
    url = FORTINET_BASE_URL + f"cmdb/firewall/address/{nombre_objeto}"
    try:
        response = requests.delete(url, headers=HEADERS, verify=VERIFY_SSL)
        response.raise_for_status()
        print(f"Objeto de dirección eliminado: {nombre_objeto}")
    except Exception as e:
        print(f"Error al eliminar el objeto de dirección {nombre_objeto}: {e}")


def main(event, context):
    
    if SOURCE.get("type") == "dns":
        ips = obtener_ips_dns(SOURCE.get("hostname"))
        print(f'Proceso iniciado a partir de una lista obtenida por un query DNS al registro {SOURCE.get("hostname")}')
    if SOURCE.get("type") == "url_response":
        ips = obtener_ips_de_url(SOURCE.get("hostname"))
        print(f'Proceso iniciado a partir de una lista obtenida por un GET a la url {SOURCE.get("hostname")}')
    
    address_objects = obtener_address_objects()
    
    # Asegura que cada IP tiene un objeto de dirección correspondiente en FortiGate
    for ip in ips:
        if f"{PREFIX_NAME_OBJ}_{ip}" not in [obj["name"] for obj in address_objects if obj.get("subnet","")!=""]:
            crear_o_actualizar_address_object(ip, address_objects)

    # Actualiza el grupo de direcciones con las nuevas IPs
    actualizar_grupo_address(ips, address_objects)

if __name__ == "__main__":
    main()

