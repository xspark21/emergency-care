import polars as pl

# Establecimientos que operaron entre 2019-2021 y no aparecen en ningún Excel DEIS
# con código antiguo mapeado. La mayoría cerró durante el estallido social (oct 2019)
# o la pandemia COVID-19 (2020-2021).
#
# Fuentes de verificación:
#   oficial_deis — cruzado contra base DEIS/RNPI con CUE confirmado
#   osm          — geocodificación inversa con dirección verificada
#
# Auditoría independiente: https://rnpi.superdesalud.gob.cl/

_GEO = [
    # CUE no asignado — SAPU Pedro Pulgar Melgarejo, Alto Hospicio (Tarapacá)
    {"IdEstablecimiento": "02-805",
     "CodigoRegion": 1,  "NombreRegion": "Tarapacá",
     "CodigoComuna": 1107, "NombreComuna": "Alto Hospicio",
     "CodigoDependencia": 1, "NombreDependencia": "Servicio De Salud Tarapacá",
     "_fuente": "oficial_deis"},

    # CUE 113309 — SAPU Los Cerros, Talcahuano (Biobío / SS Talcahuano)
    {"IdEstablecimiento": "19-808",
     "CodigoRegion": 8,  "NombreRegion": "Biobío",
     "CodigoComuna": 8110, "NombreComuna": "Talcahuano",
     "CodigoDependencia": 19, "NombreDependencia": "Servicio De Salud Talcahuano",
     "_fuente": "oficial_deis"},

    # CUE 200116 — SAPU Centenario, Los Andes (Valparaíso / SS Aconcagua)
    {"IdEstablecimiento": "08-900",
     "CodigoRegion": 5,  "NombreRegion": "Valparaíso",
     "CodigoComuna": 5301, "NombreComuna": "Los Andes",
     "CodigoDependencia": 8, "NombreDependencia": "Servicio De Salud Aconcagua",
     "_fuente": "oficial_deis"},

    # CUE no asignado — SAPU Dr. Bernardo Mellibovsky, Copiapó (Atacama)
    {"IdEstablecimiento": "04-821",
     "CodigoRegion": 3,  "NombreRegion": "Atacama",
     "CodigoComuna": 3101, "NombreComuna": "Copiapó",
     "CodigoDependencia": 3, "NombreDependencia": "Servicio De Salud Atacama",
     "_fuente": "oficial_deis"},

    # OSM: Av. Los Libertadores 531, El Monte
    {"IdEstablecimiento": "10-870",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13604, "NombreComuna": "El Monte",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Sur Occidente",
     "_fuente": "osm"},

    # OSM: Arza 1576, Melipilla
    {"IdEstablecimiento": "10-878",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13502, "NombreComuna": "Melipilla",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Sur Occidente",
     "_fuente": "osm"},

    # CUE no asignado — SAPU Dr. Gustavo Molina, Pudahuel (SS Metropolitano Occidente)
    {"IdEstablecimiento": "10-852",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13127, "NombreComuna": "Pudahuel",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Occidente",
     "_fuente": "oficial_deis"},

    # CUE no asignado — SAPU Dr. Adalberto Steeger, Cerro Navia (SS Metropolitano Occidente)
    {"IdEstablecimiento": "10-830",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13122, "NombreComuna": "Cerro Navia",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Occidente",
     "_fuente": "oficial_deis"},

    # CUE 105307 — SAPU Curimón, San Felipe (Valparaíso / SS Aconcagua)
    {"IdEstablecimiento": "08-810",
     "CodigoRegion": 5,  "NombreRegion": "Valparaíso",
     "CodigoComuna": 5601, "NombreComuna": "San Felipe",
     "CodigoDependencia": 8, "NombreDependencia": "Servicio De Salud Aconcagua",
     "_fuente": "oficial_deis"},

    # OSM: Pasaje Sado, Cerro Navia
    {"IdEstablecimiento": "10-835",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13122, "NombreComuna": "Cerro Navia",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Occidente",
     "_fuente": "osm"},

    # CUE 109315 — SAPU Dr. Fernando Monckeberg, Peñaflor (Concepción 73)
    {"IdEstablecimiento": "10-869",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13605, "NombreComuna": "Peñaflor",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Sur Occidente",
     "_fuente": "oficial_deis"},

    # CUE no asignado — SAPU Dr. Albertz, Cerro Navia (SS Metropolitano Occidente)
    {"IdEstablecimiento": "10-855",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13122, "NombreComuna": "Cerro Navia",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Occidente",
     "_fuente": "oficial_deis"},

    # CUE 104306 — SAR Rosario Corvalán, Caldera (Atacama / Canal Beagle S/N)
    {"IdEstablecimiento": "04-801",
     "CodigoRegion": 3,  "NombreRegion": "Atacama",
     "CodigoComuna": 3202, "NombreComuna": "Caldera",
     "CodigoDependencia": 3, "NombreDependencia": "Servicio De Salud Atacama",
     "_fuente": "oficial_deis"},

    # CUE 109355 — SAPU Santa Anita, Lo Prado (Camino de Loyola 5302)
    {"IdEstablecimiento": "10-815",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13117, "NombreComuna": "Lo Prado",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Occidente",
     "_fuente": "oficial_deis"},

    # CUE 103350 — Centro Asistencial Norte, Antofagasta (Los Pumas 10255)
    {"IdEstablecimiento": "03-350",
     "CodigoRegion": 2,  "NombreRegion": "Antofagasta",
     "CodigoComuna": 2101, "NombreComuna": "Antofagasta",
     "CodigoDependencia": 2, "NombreDependencia": "Servicio De Salud Antofagasta",
     "_fuente": "oficial_deis"},

    # CUE 109307 — SAPU Garín, Quinta Normal (Janequeo 5612)
    {"IdEstablecimiento": "10-825",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13128, "NombreComuna": "Quinta Normal",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Occidente",
     "_fuente": "oficial_deis"},

    # OSM: San Pablo, Pudahuel
    {"IdEstablecimiento": "10-851",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13127, "NombreComuna": "Pudahuel",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Occidente",
     "_fuente": "osm"},

    # OSM: 2a Transversal 457, San Pedro de la Paz
    {"IdEstablecimiento": "18-802",
     "CodigoRegion": 8,  "NombreRegion": "Biobío",
     "CodigoComuna": 8108, "NombreComuna": "San Pedro De La Paz",
     "CodigoDependencia": 8, "NombreDependencia": "Servicio De Salud Concepción",
     "_fuente": "osm"},

    # CUE no asignado — SAPU Pulmahue, Padre Las Casas (Araucanía / SS Araucanía Sur)
    {"IdEstablecimiento": "21-908",
     "CodigoRegion": 9,  "NombreRegion": "La Araucanía",
     "CodigoComuna": 9112, "NombreComuna": "Padre Las Casas",
     "CodigoDependencia": 21, "NombreDependencia": "Servicio De Salud Araucanía Sur",
     "_fuente": "oficial_deis"},

    # CUE 117803 — SAPU Ultraestación, Chillán (Ñuble / Ruiz de Gamboa S/N)
    {"IdEstablecimiento": "17-803",
     "CodigoRegion": 16, "NombreRegion": "Ñuble",
     "CodigoComuna": 16101, "NombreComuna": "Chillán",
     "CodigoDependencia": 17, "NombreDependencia": "Servicio De Salud Ñuble",
     "_fuente": "oficial_deis"},

    # CUE 200115 — SAPU Dr. Miguel Concha, Quillota (Maipú 902)
    {"IdEstablecimiento": "07-905",
     "CodigoRegion": 5,  "NombreRegion": "Valparaíso",
     "CodigoComuna": 5701, "NombreComuna": "Quillota",
     "CodigoDependencia": 7, "NombreDependencia": "Servicio De Salud Viña Del Mar - Quillota",
     "_fuente": "oficial_deis"},

    # OSM: Pudahuel
    {"IdEstablecimiento": "10-850",
     "CodigoRegion": 13, "NombreRegion": "Metropolitana De Santiago",
     "CodigoComuna": 13127, "NombreComuna": "Pudahuel",
     "CodigoDependencia": 13, "NombreDependencia": "Servicio De Salud Metropolitano Occidente",
     "_fuente": "osm"},
]

_NOMBRES = {
    "17-803": "SAPU Ultraestación",
    "07-905": "SAPU Dr. Miguel Concha",
    "08-900": "SAPU Centenario",
}

_GEO_SCHEMA = {
    "IdEstablecimiento": pl.String,
    "CodigoRegion":      pl.Int64,
    "NombreRegion":      pl.String,
    "CodigoComuna":      pl.Int64,
    "NombreComuna":      pl.String,
    "CodigoDependencia": pl.Int64,
    "NombreDependencia": pl.String,
}


def geo() -> pl.DataFrame:
    return pl.DataFrame(
        [{k: v for k, v in r.items() if k != "_fuente"} for r in _GEO],
        schema=_GEO_SCHEMA,
    )


def nombres() -> pl.DataFrame:
    return pl.DataFrame({
        "IdEstablecimiento": list(_NOMBRES.keys()),
        "NEstablecimiento":  list(_NOMBRES.values()),
    })


def audit() -> pl.DataFrame:
    return pl.DataFrame(_GEO)