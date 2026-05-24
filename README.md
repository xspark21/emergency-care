# Emergency Care

Consolidación de los registros de atenciones de urgencia del sistema público
chileno (DEIS/SADU), 2019–2025.

Los archivos publicados por el DEIS están codificados en latin-1, tienen esquema
variable entre períodos y carecen de información geográfica antes de 2023. Este
repositorio resuelve los tres problemas y produce una base analizable en formato
Parquet con cobertura geográfica completa para todo el período.

El mapeo semántico hacia CIE-11 vive en [`deis-cie11`](https://github.com/xspark21/deis-cie11),
incluido como submódulo. La motivación, decisiones de diseño y limitaciones de la
base se describen en [`informe.pdf`](informe.pdf).

---

## Uso rápido

```python
import polars as pl
lf = pl.scan_parquet("data/final/emergency_care_curated.parquet")
```

Compatible con pandas, DuckDB y R (`arrow::read_parquet`).

---

## Salida

| Archivo | Descripción |
|---|---|
| `data/final/urgencias_deis_YYYY_YYYY.parquet` | Base maestra consolidada, lista para análisis |
| `data/reference/establecimientos.parquet` | Catálogo de establecimientos |
| `data/reference/cat_geo.parquet` | Catálogo geográfico interno |
| `data/reference/cat_nombres.parquet` | Catálogo de nombres interno |

---

## Datos necesarios

`data/raw/`
- `AtencionesUrgencia2019.csv` … `AtencionesUrgencia2025.csv`
- Fuente: [DEIS — Datos Abiertos](https://deis.minsal.cl/#datosabiertos)

`data/reference/`
- `Copia-de-Establecimientos-DEIS-MINSAL-18-02-2025.xlsx`
- `Establecimientos-DEIS-MINSAL-07-01-2026.xlsx`
- Fuente: [MINSAL — Catálogo de Establecimientos](https://estadistica.ssmso.cl/download/establecimientos-deis-minsal/)

Se recomienda incluir ambos Excel ya que el de 2026 cubre establecimientos cerrados
no presentes en la versión anterior.

`deis-cie11/data/raw/`
- `LinearizationMiniOutput-MMS-en.xlsx`
- Fuente: [OMS — CIE-11 MMS Linearization](https://icd.who.int/browse/2024-01/mms)

> `deis-cie11` fue construido sobre el vocabulario de glosas 2019–2025. Años
> posteriores requieren actualización del resolver semántico.

---

## Instalación

```bash
git clone --recurse-submodules https://github.com/xspark21/emergency-care.git
cd emergency-care
uv sync
```

Requiere Python ≥ 3.14 y [uv](https://github.com/astral-sh/uv).

---

## Uso

```bash
make build      # construye la base
make validate   # verifica integridad
make cie11      # copia la base al submódulo y ejecuta el pipeline CIE-11
make all        # los tres en secuencia
```

Para incorporar un año nuevo: agregar el CSV en `data/raw/`, actualizar los Excel
DEIS si corresponde, y ejecutar `make build`. El nombre del parquet se actualiza
automáticamente.

---

## Estructura

```
emergency-care/
├── build.py
├── Makefile
├── informe.pdf
├── data/
│   ├── raw/            # CSV originales (no incluidos)
│   ├── utf8_fixed/     # generado
│   ├── final/          # generado
│   └── reference/
├── deis-cie11/         # submódulo
├── scripts/
│   └── validate.py
└── src/
    ├── config.py
    ├── io.py
    ├── clean.py
    ├── catalog.py
    ├── deis.py
    ├── locality.py
    ├── no_register.py
    └── modules.py
```

---

## Limitaciones

22 establecimientos no aparecen en ningún catálogo oficial del DEIS. Su información
geográfica fue verificada manualmente y está documentada en `src/no_register.py`.
Representan el 2,7% de los establecimientos y el 0,6% de los registros.

3 establecimientos activos en 2024–2025 no aparecen en ningún catálogo público con
correspondencia histórica de códigos. Su geografía y nombre fueron verificados
mediante fuentes públicas y están documentados en `src/no_register.py`.

> El análisis estadístico sobre esta base se encuentra en desarrollo en un repositorio separado.

---

## Fuentes

- DEIS — Atenciones de Urgencia: https://deis.minsal.cl/#datosabiertos
- MINSAL — Catálogo de Establecimientos: https://estadistica.ssmso.cl/download/establecimientos-deis-minsal/
- OMS — CIE-11 MMS Linearization: https://icd.who.int/browse/2024-01/mms
- Manual de Registro SADU v1.1 — DEIS, diciembre 2020