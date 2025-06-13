# Título del Proyecto (en Español)

Esta es una breve descripción del proyecto en español.

## Requisitos Previos (Windows)

- Python 3.x
- Git

## Instalación

1.  Clona el repositorio:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd nombre-del-directorio-clonado
    ```
2.  Crea un entorno virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r noox_pkg/requirements.txt
    ```

## Uso (GUI)

Ejecuta la GUI con:
```bash
python -m noox_pkg.main gui
# o simplemente
python -m noox_pkg.main
```

## Uso (CLI)

Consulta la ayuda para los comandos:
```bash
python -m noox_pkg.main --help
```

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `noox_pkg/LICENSE` para más detalles.
