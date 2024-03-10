# Actualización de Grupos de Direcciones en Fortinet

Este proyecto proporciona una herramienta para la gestión automática de grupos de direcciones en sistemas Fortinet, asegurando que estén actualizados con las direcciones IP o nombres de host más recientes. Es especialmente útil en entornos dinámicos donde las direcciones de servidores o servicios pueden cambiar frecuentemente.

## Características

- **Automatización**: Sincroniza los miembros de un grupo de direcciones con las últimas direcciones IP o nombres de host automáticamente.
- **Gestión Eficiente**: Permite la creación de grupos de direcciones si estos no existen, facilitando la administración centralizada.
- **Flexibilidad**: Soporta diferentes fuentes para la actualización de direcciones, incluyendo DNS y respuestas de URL.

## Casos de Uso

### Caso 1: Sincronización con DNS Query

Para actualizar un grupo de direcciones basado en los registros DNS del tipo A de un hostname, como `servers.deploybot.com`, se puede implementar un enfoque que resuelva estos nombres a sus direcciones IP actuales.

```python
# Ejemplo de función para resolver DNS y actualizar el grupo
SOURCE = { "type": "dns", "hostname": "servers.deploybot.com"}
```

### Caso 2: Sincronización con Respuesta de URL

Cuando las direcciones IP relevantes se publican a través de una API o un servicio web, el script puede actualizar el grupo de direcciones basándose en la respuesta de una URL específica.

```python
# Ejemplo de función para obtener IPs de una URL y actualizar el grupo
SOURCE = { "type": "url_response", "hostname": "https://www.cloudflare.com/ips-v4/#"}
```

## Configuración e Instalación
Accede al artículo completo con todos los detalles para implementarlo en GCP usando serverless!

https://medium.com/@gortega/introducción-ff5f969c6f58

---


# Address Group Updates in Fortinet
This project provides a tool for the automatic management of address groups in Fortinet systems, ensuring they are up-to-date with the most recent IP addresses or hostnames. It is particularly useful in dynamic environments where the addresses of servers or services may change frequently.

## Features
- **Automation**: Synchronizes the members of an address group with the latest IP addresses or hostnames automatically.
- **Efficient Management**: Allows the creation of address groups if they do not exist, facilitating centralized administration.
- **Flexibility**: Supports different sources for updating addresses, including 
DNS and URL response queries.

## Use Cases
### Case 1: Synchronization with DNS Query
To update an address group based on the A type DNS records of a hostname, such as `servers.deploybot.com`, an approach that resolves these names to their current IP addresses can be implemented.

```python
# Example function for DNS resolution and group updating
SOURCE = {"type": "dns", "hostname": "servers.deploybot.com"}
```

### Case 2: Synchronization with URL Response
When the relevant IP addresses are published through an API or web service, the script can update the address group based on the response from a specific URL.

```python
# Example function to fetch IPs from a URL and update the group
SOURCE = {"type": "url_response", "hostname": "https://www.cloudflare.com/ips-v4/#"}
```

## Configuration and Installation
Access the full article with all the details to implement it on GCP using serverless!

https://gortega.medium.com/automate-ip-address-objects-updating-in-fortinet-using-gcp-python-and-serverless-49b67028c3db
