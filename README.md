# La Ganga Bot

Bot de Twitter (preparado parafuturas redes sociales) para publicar "Flash Deals" de La Ganga Ofertas automáticamente.

## 🚀 Cómo Funciona

1. **Obtención de Ofertas**: El bot consulta la API de Flash Deals (`endpoint.py`).
2. **Filtrado**: Compara las ofertas obtenidas con una base de datos local (`sqlite_store.py`) para identificar cuáles ya han sido publicadas.
3. **Selección**: Elige la mejor oferta disponible (mayor porcentaje de descuento) de las que no han sido publicadas.
4. **Procesamiento de Imagen**: Descarga la imagen del producto y le añade un badge con el descuento, marca de agua y footer con logo (`image_processor.py`).
5. **Publicación**: Formatea el mensaje (`logic.py`) y utiliza la API de Twitter (`twitter.py`) para publicar el tweet con la imagen procesada.
6. **Persistencia**: Marca la oferta como publicada en la base de datos local y, si se ejecuta en GitHub Actions, hace un commit de la base de datos actualizada para mantener el historial.

## 📂 Estructura del Proyecto

El código fuente se encuentra en `src/laganga_bot/`:

- **`domain/`**:
    - `models.py`: Definiciones de datos (e.g., `Deal`).
    - `logic.py`: Lógica de negocio pura (filtrado, selección, formateo).
- **`fetch/`**:
    - `endpoint.py`: Lógica para conectar con la API de ofertas.
- **`publish/`**:
    - `twitter.py`: Cliente para interactuar con la API de Twitter.
    - `image_processor.py`: Lógica de manipulación de imágenes (watermarks, badges).
    - `logo.png`: Logo utilizado en el footer de las imágenes.
- **`state/`**:
    - `sqlite_store.py`: Manejo de la base de datos SQLite para evitar duplicados.
    - `bot_history.db`: Archivo de base de datos (se genera al ejecutar).
- **`settings.py`**: Configuración centralizada y validación de variables de entorno.
- **`logging.py`**: Configuración de logs.
- **`main.py`**: Script principal que orquesta todo el flujo.

## 🛠️ Configuración

Este proyecto utiliza `uv` como gestor de paquetes.

### Variables de Entorno (.env)

Crea un archivo `.env` con las siguientes variables:

```ini
FLASH_DEALS_API_URL=https://...
TWITTER_API_KEY=...
TWITTER_API_KEY_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_TOKEN_SECRET=...
# Opcional: Para probar sin publicar
DRY_RUN=True 
```

### Ejecutar Localmente

1. Instalar dependencias (incluye `tweepy`, `pillow`, etc.):
   ```bash
   uv sync
   ```
2. Ejecutar el bot de prueba (Dry Run):
   Asegúrate de tener `DRY_RUN=True` en tu `.env` o pásalo como variable:
   ```bash
   uv run python -m laganga_bot.main
   ```
3. Limpiar historial de publicados manualmente:
   ```bash
   uv run python -m laganga_bot.main --clear-db
   ```

### Tests

Para ejecutar los tests unitarios:

```bash
uv run python -m unittest discover tests
```

Para probar visualmente el procesamiento de imágenes:

```bash
uv run python tests/visual_test.py
```

Para inspeccionar y/o vaciar la base de datos interactivamente:

```bash
uv run python state/inspect_db.py
```

## 🔄 Automatización (GitHub Actions)

- **Publicación Diaria**: El workflow `.github/workflows/twitter_bot.yml` ejecuta el bot diariamente a las 17:00 (Hora Argentina). Se encarga de guardar el estado (`bot_history.db`) en el repositorio.
- **Limpieza de Historial**: El workflow `.github/workflows/cleanup_db.yml` se ejecuta el 1 y 15 de cada mes para vaciar la base de datos de ofertas publicadas, permitiendo que ofertas antiguas vuelvan a ser elegibles.
