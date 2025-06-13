# Título del Proyecto (en Español)

Esta es una breve descripción del proyecto en español.

## Requisitos Previos (Windows)

- Python 3.x
- Git

## Instalación

1.  Clona el repositorio:
    ```bash
    git clone https://github.com/estrosebas/noox-pkg
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

## Uso (Interfaz Gráfica - GUI)

Ejecuta la GUI con:
```bash
python -m noox_pkg.main gui
# o simplemente (si no se especifica ningún comando)
python -m noox_pkg.main
```

La interfaz gráfica te permite:
*   **Importar JSON**: Carga una lista de aplicaciones desde un archivo JSON.
*   **Descargar Seleccionado**: Descarga la aplicación que hayas seleccionado en la lista.
*   **Descargar Todo**: Descarga todas las aplicaciones de la lista.
*   **Establecer Directorio de Descarga**: Elige dónde se guardarán los archivos descargados.
*   **Selector de Esquema de Color**: Utiliza el menú desplegable (ComboBox) ubicado encima de la barra de estado para cambiar la paleta de colores de la interfaz (ej. "Neon Verde", "Neon Azul"). La estructura oscura general se mantiene, pero los colores de acento y resaltado cambiarán.
*   **Barra de Progreso de Descarga**: Durante las descargas activas, una barra de progreso aparecerá encima de la barra de estado, mostrando el avance del archivo actual.


## Uso (CLI)

Consulta la ayuda para los comandos:
```bash
python -m noox_pkg.main --help
```

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `noox_pkg/LICENSE` para más detalles.
