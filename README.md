# emergency care

Consolidación de los registros históricos de atenciones de urgencia del sistema
público chileno (DEIS/SADU), 2019–2025.

El repositorio construye una base analizable a partir de los CSV anuales publicados
por el DEIS, resolviendo tres problemas estructurales presentes en los archivos de
origen: encoding latin-1, esquema variable entre períodos, e información geográfica
ausente en los registros anteriores a 2023.

El mapeo semántico hacia CIE-11 vive en [`deis-cie11`](https://github.com/xspark21/deis-cie11)
(incluido como submodulo).  


---

## Qué genera

| Archivo | Descripción |
|---|---|
| `data/final/urgencias_deis_YYYY_YYYY.parquet` | Base maestra consolidada |
| `data/reference/establecimientos.parquet` | Catálogo de establecimientos con trazabilidad |
| `data/reference/cat_geo.parquet` | Catálogo geográfico interno |
| `data/reference/cat_nombres.parquet` | Catálogo de nombres interno |

Cobertura de la base maestra:

| Métrica | Valor |
|---|---|
| Registros totales | 55.659.765 |
| Años cubiertos | 2019 – 2025 |
| Establecimientos | 805 |
| Nulos en CodigoRegion | 0 |
| Nulos en CodigoComuna | 0 |

---

## Contexto

Los CSV publicados por el DEIS presentan tres características que requieren
tratamiento previo al análisis:

**Encoding.** Los archivos vienen en latin-1. La conversión a UTF-8 se hace con
el módulo `csv` estándar de Python, sin pérdida de información.

**Esquema variable.** Los archivos 2019–2022 tienen 15 columnas. Los archivos
2023–2025 tienen 21. Las columnas geográficas (`CodigoRegion`, `NombreRegion`,
`CodigoComuna`, `NombreComuna`, `CodigoDependencia`, `NombreDependencia`) no
existen en los años anteriores. El pipeline concatena diagonalmente y recupera
esa información en cascada.

**Geografía incompleta.** La ausencia de columnas geográficas en 2019–2022 es
una característica del formulario SADU de ese período. La recuperación opera en
cuatro etapas:

1. Valor propio de la fila (disponible en 2023+)
2. Último valor conocido por establecimiento extraído de los propios CSV
3. Catálogos Excel del MINSAL (activos y cerrados, versiones 2025 y 2026)
4. Tabla de verificación manual para 22 establecimientos sin cobertura en
   ninguna fuente automatizable (`src/sin_registro.py`)

Los 22 establecimientos en `sin_registro.py` corresponden principalmente a SAPU
que operaron entre 2019–2021. La ubicación de cada uno se verificó manualmente
mediante búsqueda en fuentes públicas y Google Maps. Cada entrada está documentada
con su fuente (`oficial_deis` u `osm`) en el mismo archivo.

---

## Limitaciones

El pipeline recupera la información disponible en las fuentes públicas del DEIS.
Hay casos que quedan fuera de ese alcance:

- 3 establecimientos activos en 2024–2025 (`07-905`, `17-803`, `08-900`) no
  tienen nombre en ningún catálogo publicado a la fecha de construcción de la base.
  Sus registros clínicos y geográficos están completos.

- 22 establecimientos tienen geografía asignada mediante verificación manual.
  Aunque cada entrada fue contrastada con fuentes públicas, no proviene de un
  registro oficial estructurado y podría contener imprecisiones.

- El pipeline está diseñado para los CSV 2019–2025. Años futuros se incorporan
  agregando el CSV correspondiente en `data/raw/`, pero el submodulo `deis-cie11`
  requiere actualización independiente ya que su resolver semántico fue construido
  sobre el vocabulario de glosas de ese período.

- Los datos de origen son administrativos. El pipeline no corrige ni reinterpreta
  el contenido clínico de los registros.

---

## Estructura

```
emergency-care/
├── build.py                  # punto de entrada
├── Makefile
├── data/
│   ├── raw/                  # CSV originales del DEIS (no incluidos en el repo)
│   ├── utf8_fixed/           # CSV convertidos (generado)
│   ├── final/                # base maestra (generado)
│   └── reference/            # catálogos de establecimientos
├── deis-cie11/               # submodulo — mapeo semántico hacia CIE-11
├── scripts/
│   └── validate.py
└── src/
    ├── config.py
    ├── io.py
    ├── clean.py
    ├── catalog.py
    ├── deis.py
    ├── locality.py
    ├── sin_registro.py
    └── modules.py
```

---

## Uso

### Requisitos

- Python ≥ 3.14
- [uv](https://github.com/astral-sh/uv)

### Datos necesarios

`data/raw/` — CSV de atenciones de urgencia 2019–2025:
- `AtencionesUrgencia2019.csv` … `AtencionesUrgencia2025.csv`
- Fuente: [DEIS — Datos Abiertos](https://deis.minsal.cl/#datosabiertos)

`data/reference/` — catálogos de establecimientos MINSAL:
- `Copia-de-Establecimientos-DEIS-MINSAL-18-02-2025.xlsx`
- `Establecimientos-DEIS-MINSAL-07-01-2026.xlsx`
- Fuente: https://estadistica.ssmso.cl/download/establecimientos-deis-minsal/

Se recomienda incluir ambos Excel ya que el de 2026 contiene establecimientos
cerrados no presentes en la versión anterior.

`deis-cie11/data/raw/` — archivo OMS para el submodulo:
- `LinearizationMiniOutput-MMS-en.xlsx`
- Fuente: [OMS — CIE-11 MMS Linearization](https://icd.who.int/browse/2024-01/mms)

> El submodulo `deis-cie11` fue construido sobre el vocabulario de glosas
> 2019–2025. Si se agregan años posteriores, el resolver semántico requiere
> actualización independiente.

### Instalación

```bash
git clone --recurse-submodules https://github.com/xspark21/emergency-care.git
cd emergency-care
uv sync
```

### Ejecución

```bash
make build      # construye la base
make validate   # verifica integridad
make cie11      # copia la base al submodulo y ejecuta el pipeline CIE-11
make all        # los tres en secuencia
```

### Mantenimiento

El pipeline no tiene años hardcodeados. Para incorporar un año nuevo:

1. Agregar el CSV correspondiente en `data/raw/`
2. Actualizar los Excel DEIS si el MINSAL publicó versión nueva
3. Ejecutar `make build`

El nombre del parquet final se actualiza automáticamente.

---

## Fuentes

- DEIS — Atenciones de Urgencia: https://deis.minsal.cl/#datosabiertos
- MINSAL — Catálogo de Establecimientos: https://estadistica.ssmso.cl/download/establecimientos-deis-minsal/
- OMS — CIE-11 MMS Linearization: https://icd.who.int/browse/2024-01/mms
- Manual de Registro SADU v1.1 — DEIS, diciembre 2020