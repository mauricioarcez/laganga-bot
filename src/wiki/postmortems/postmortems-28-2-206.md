# Postmortem: Error 403 Forbidden en Bot de Twitter

## Fecha
28 de Febrero de 2026

## Incidente
El workflow de GitHub Actions fallaba consistentemente al intentar publicar los deals (ofertas) en Twitter. El error arrojado por el proceso era:
```
tweepy.errors.Forbidden: 403 Forbidden
```
Específicamente, este error ocurría en el método `self.client.create_tweet` al utilizar la API v2 de Twitter a través de la librería `tweepy`.

## Análisis Causa Raíz
Tras revisar la configuración del flujo de GitHub Actions y el código en Python (`twitter.py`), se determinó que la lógica era correcta y realizaba la autenticación de "OAuth 1.0a User Context" de manera adecuada (necesaria para la carga previa de contenido multimedia).

El problema radicaba exclusivamente en la configuración de la aplicación dentro del **Portal de Desarrolladores de Twitter**. Un error `403 Forbidden` al invocar `create_tweet` bajo estas circunstancias indica que la App no cuenta con los permisos de escritura ("Write") para publicar, o bien, que los *Access Tokens* configurados habían sido generados antes de que a la App se le concedieran dichos permisos de escritura (manteniendo así, únicamente, sus permisos originales de solo lectura).

## Solución y Pasos de Resolución
Para solucionar este inconveniente y permitir que el bot publique en Twitter, se documentan los siguientes pasos que deben ser ejecutados:

1. **Actualizar Permisos de la App:** Ingresar al [Portal de Desarrolladores de Twitter](https://developer.twitter.com/en/portal/dashboard). En la sección de configuración de la App ("User authentication settings"), editar los permisos para cambiar de "Read" (lectura) a **"Read and write"** (lectura y escritura) o a "Read, write, and Direct Messages".
2. **Regenerar Tokens y Claves:** Como los tokens preexistentes no heredan los nuevos permisos automáticamente, es indispensable regenerarlos. Ir a la pestaña "Keys and tokens" y regenerar tanto los **Access Token and Secret** como también, idealmente, las **Consumer Keys (API Key and Secret)**.
3. **Actualizar Secretos en GitHub:** Tomar esos 4 nuevos valores generados y sobrescribir los secretos en el repositorio de GitHub (Settings -> Secrets and variables -> Actions):
   - `TWITTER_API_KEY`
   - `TWITTER_API_KEY_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`

## Lecciones Aprendidas
Cualquier modificación en los permisos/alcances (scopes) de una aplicación en Twitter Developer requiere **siempre** la regeneración completa de sus tokens y claves de acceso. Si los tokens fueron generados en un estado de "Solo Lectura", la API denegará permanentemente cualquier intento de publicación devolviendo un código 403, independientemente de si el código de la aplicación está correcto.
