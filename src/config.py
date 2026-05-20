from pathlib import Path
import polars as pl

DATA_DIR  = Path("data")
RAW_DIR   = DATA_DIR / "raw"
FIXED_DIR = DATA_DIR / "utf8_fixed"
FINAL_DIR = DATA_DIR / "final"
REF_DIR   = DATA_DIR / "reference"

def _year_range() -> str:
    years = sorted(
        int(f.stem.replace("AtencionesUrgencia", ""))
        for f in RAW_DIR.glob("AtencionesUrgencia*.csv")
    )
    return f"{years[0]}_{years[-1]}" if years else "2019_2025"

MASTER_PARQUET  = FINAL_DIR / f"urgencias_deis_{_year_range()}.parquet"
EST_PARQUET     = REF_DIR / "establecimientos.parquet"
CAT_GEO         = REF_DIR / "cat_geo.parquet"
CAT_NOMBRES     = REF_DIR / "cat_nombres.parquet"

DEIS_2025 = REF_DIR / "Copia-de-Establecimientos-DEIS-MINSAL-18-02-2025.xlsx"
DEIS_2026 = REF_DIR / "Establecimientos-DEIS-MINSAL-07-01-2026.xlsx"

# Columnas presentes en todos los años. Las geo (CodigoRegion, etc.) solo aparecen
# desde 2023 — diagonal_concat rellena con null los años anteriores.
CSV_SCHEMA = {
    "IdEstablecimiento":      pl.String,
    "NEstablecimiento":       pl.String,
    "IdCausa":                pl.Int64,
    "GlosaCausa":             pl.String,
    "Total":                  pl.Int64,
    "Menores_1":              pl.Int64,
    "De_1_a_4":               pl.Int64,
    "De_5_a_14":              pl.Int64,
    "De_15_a_64":             pl.Int64,
    "De_65_y_mas":            pl.Int64,
    "fecha":                  pl.String,
    "semana":                 pl.Int64,
    "GLOSATIPOESTABLECIMIENTO": pl.String,
    "GLOSATIPOATENCION":      pl.String,
    "GlosaTipoCampana":       pl.String,
    "CodigoRegion":           pl.Int64,
    "NombreRegion":           pl.String,
    "CodigoDependencia":      pl.Int64,
    "NombreDependencia":      pl.String,
    "CodigoComuna":           pl.Int64,
    "NombreComuna":           pl.String,
}

# Nombres de columna en los Excel DEIS varían entre versiones y hojas.
# Este mapa unifica todo a nombres internos consistentes.
DEIS_COL_MAP = {
    "Código Antiguo":                                             "id_antiguo",
    "Código Vigente":                                             "id_vigente",
    "Código  Madre Antiguo":                                      "id_madre_antiguo",
    "Código Madre Nuevo":                                         "id_madre_nuevo",
    "Código  Madre":                                              "id_madre_antiguo",
    "Código Nuevo Madre":                                         "id_madre_nuevo",
    "Código Región":                                              "CodigoRegion",
    "Nombre Región":                                              "NombreRegion",
    "Código Comuna":                                              "CodigoComuna",
    "Nombre Comuna":                                              "NombreComuna",
    "Código Dependencia Jerárquica (SEREMI / Servicio de Salud)": "CodigoDependencia",
    "Nombre Dependencia Jerárquica (SEREMI / Servicio de Salud)": "NombreDependencia",
    "Dependencia Jerárquica (SEREMI / Servicio de Salud)":        "NombreDependencia",
    "Nombre Oficial":                                             "NEstablecimiento",
    "Tipo Establecimiento (Unidad)":                              "TipoEstablecimiento",
    "Tipo Establecimiento":                                       "TipoEstablecimiento",
    "Ámbito de Funcionamiento":                                   "AmbitoFuncionamiento",
    "Ambito de Funcionamiento":                                   "AmbitoFuncionamiento",
    "Dependencia Administrativa":                                 "DependenciaAdministrativa",
    "Pertenencia al SNSS":                                        "PertenenciaSNSS",
    "Nivel de Atención":                                          "NivelAtencion",
    "Nivel de Complejidad":                                       "NivelComplejidad",
    "Certificación":                                              "Certificacion",
    "Tiene Servicio de Urgencia":                                 "TieneUrgencia",
    "Tipo de Urgencia":                                           "TipoUrgencia",
    "Tipo  de Urgencia":                                          "TipoUrgencia",
    "Clasificcion Tipo de SAPU":                                  "TipoSAPU",
    "Clasificación Tipo de SAPU":                                 "TipoSAPU",
    "Tipo  de SAPU":                                              "TipoSAPU",
    "Modalidad de Atención":                                      "ModalidadAtencion",
    "Tipo de Atención":                                           "ModalidadAtencion",
    "Vía":                                                        "Via",
    "Número":                                                     "Numero",
    "Dirección":                                                  "Direccion",
    "Teléfono":                                                   "Telefono",
    "LATITUD      [Grados decimales]":                            "Latitud",
    "LATITUD [Grados decimales]":                                 "Latitud",
    "LONGITUD [Grados decimales]":                                "Longitud",
    "Estado de Funcionamiento":                                   "EstadoFuncionamiento",
    "Tipo de Prestador Sistema de Salud":                         "TipoPrestador",
    "Fecha Inicio Funcionamiento":                                "FechaInicio",
    "Fecha de Funcionamiento":                                    "FechaInicio",
    "Fecha de Incorporación a la base":                           "FechaIncorporacion",
    "Fecha de cierre/ Fecha en que se hace el cambio en BD":      "FechaCierre",
}

EST_COLS = [
    "id_antiguo", "id_vigente", "id_madre_antiguo", "id_madre_nuevo",
    "NEstablecimiento", "TipoEstablecimiento", "AmbitoFuncionamiento",
    "PertenenciaSNSS", "DependenciaAdministrativa", "NivelAtencion", "NivelComplejidad",
    "CodigoRegion", "NombreRegion", "CodigoComuna", "NombreComuna",
    "CodigoDependencia", "NombreDependencia",
    "Via", "Numero", "Direccion", "Telefono",
    "Latitud", "Longitud",
    "TieneUrgencia", "TipoUrgencia", "TipoSAPU", "ModalidadAtencion", "TipoPrestador",
    "Certificacion", "FechaInicio", "FechaCierre", "FechaIncorporacion",
    "activo",
]

GEO_COLS = [
    "CodigoRegion", "NombreRegion", "CodigoComuna", "NombreComuna",
    "CodigoDependencia", "NombreDependencia",
]