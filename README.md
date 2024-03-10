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