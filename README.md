# TrendGear Dashboard

Proyecto desarrollado siguiendo la **Guía Metodológica del Taller "TrendGear Dashboard – De la Data Sintética a la Web Funcional"**, aplicando sus tres fases: ingeniería de datos, maquetación ágil e integración con Firebase.

## Estructura del proyecto

```
trendgear/
├── index.html              # Estructura: header, main, footer
├── css/
│   └── style.css           # Esquema negro + verde, responsive
├── js/
│   └── script.js           # Fetch, renderizado dinámico, filtros
├── data/
│   ├── generate_dataset.py # Generador y validador (4 pasos)
│   ├── dataset.csv
│   ├── dataset.psv
│   └── dataset.json        # Estructura tipo Firebase Realtime DB
└── README.md
```

## Fase I — Dataset sintético

`data/generate_dataset.py` implementa los 4 pasos de la guía:

1. **Crear muestra**: 8 registros de referencia escritos a mano (`SEED_SAMPLE`).
2. **Limpiar muestra**: `clean_row()` normaliza `Payment Method` y `Membership Status`.
3. **One-shot prompting**: `expand_dataset()` aprende el patrón de la muestra y lo escala a 60 registros, controlando distribuciones (edad con `random.gauss`, montos siempre positivos, fecha de compra ≤ último login).
4. **Revisión**: `validate_dataset()` corre el checklist completo (rangos numéricos, formato ISO de fechas, categorías normalizadas, IDs únicos, dominio de correo seguro `example.com`, ciudad dentro del catálogo). Resultado: **0 inconsistencias**.

Las 11 columnas obligatorias están cubiertas: Customer ID, Name, Email, Product Purchased, Purchase Date, Amount Spent ($), Age, City, Payment Method, Last Login Date, Membership Status.

## Fase II — Maquetación

Estructura en `header` / `main` / `footer`, código segregado en HTML, CSS y JS independientes. Esquema de color solicitado: **negro** (`#0a0a0a` fondo, `#151b15` tarjetas) y **verde** (`#00e676` acento). Tipografía Roboto para texto y Roboto Mono para datos numéricos (IDs, montos, fechas). Navegación responsiva con menú hamburguesa por debajo de 720px.

## Fase III — Integración de datos

`js/script.js` hace `fetch()` asíncrono a `data/dataset.json`, que reproduce la estructura de un nodo de **Firebase Realtime Database** (`{ "TG-0001": {...}, ... }`). El comentario en el código señala exactamente qué línea cambiar (`FIREBASE_URL`) para apuntar a una base de datos real en la nube. Los registros se recorren con `forEach` y cada fila de la tabla se genera con un *template literal*, incluyendo búsqueda, filtro por membresía y ordenamiento.

## Cómo ejecutarlo

```bash
cd trendgear
python3 -m http.server 8000
# abrir http://localhost:8000
```

---

## Prompt utilizado para generar este proyecto

> Actúa como Consultor Senior en Transformación Digital y desarrolla el taller "TrendGear Dashboard – De la Data Sintética a la Web Funcional" siguiendo exactamente la guía metodológica adjunta, paso por paso:
>
> **Fase I — Datos sintéticos:** crea un dataset con las 11 columnas obligatorias (Customer ID, Name, Email, Product Purchased, Purchase Date, Amount Spent ($), Age, City, Payment Method, Last Login Date, Membership Status) siguiendo la metodología de 4 pasos (crear muestra, limpiar muestra, one-shot prompting, revisión). Usa un dominio de correo seguro y valida el dataset contra el checklist de integridad de la guía (rangos, formatos ISO, categorías normalizadas, unicidad, coherencia cruzada).
>
> **Fase II — Maquetación:** construye el Dashboard con código segregado (HTML, CSS y JS en archivos independientes), estructura de header/main/footer, navegación responsiva con menú hamburguesa en móvil, y tipografía Roboto. En lugar del esquema de colores sugerido en la guía, usa **negro y verde** como paleta principal.
>
> **Fase III — Integración:** conecta el frontend a los datos mediante un `fetch` asíncrono que simule la estructura de Firebase Realtime Database, renderiza los registros dinámicamente con `forEach` y template literals, e incluye filtros de búsqueda, membresía y ordenamiento.
>
> Entrega todos los archivos del proyecto y un README que explique cómo se aplicó cada fase de la guía.
