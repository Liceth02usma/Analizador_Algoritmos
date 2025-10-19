

#  Backend - FastAPI

##  Requisitos previos

* [Python 3.10+](https://www.python.org/downloads/)
* [pip](https://pip.pypa.io/en/stable/) o [pipenv/venv] para entornos virtuales
* [Uvicorn](https://www.uvicorn.org/) (servidor ASGI)

---

##  Instalación

1. Clona el repositorio o descarga el proyecto:

   ```bash
   git clone https://github.com/tu-usuario/Analizador_Algoritmos.git
   cd Analizador_Algoritmos/backend
   ```


2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

---

##  Ejecución del servidor

Ejecuta el siguiente comando desde la carpeta `backend`:

```bash
uvicorn app.main:app --reload
```

* `--reload`: recarga automática al modificar el código.
* El servidor correrá en  [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

##  Documentación automática

FastAPI genera documentación interactiva automáticamente:

* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Redoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Tests

Permite correr las pruebas del proyecto

```bash
$ pytest -q
```
