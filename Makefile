# Makefile — emergency_care
BOLD  := \033[1m
RESET := \033[0m

.PHONY: help build validate cie11 all clean

help:
	@printf "\n$(BOLD):: emergency_care$(RESET)\n\n"
	@printf "  build      construye urgencias_deis_YYYY_YYYY.parquet\n"
	@printf "  validate   verifica integridad de la base\n"
	@printf "  cie11      copia la base al submodulo y ejecuta el pipeline CIE-11\n"
	@printf "  all        build + validate + cie11\n"
	@printf "  clean      elimina archivos generados\n"
	@printf "\n"

build:
	@printf "\n:: emergency_care — build\n"
	@uv run build.py

validate:
	@printf "\n:: emergency_care — validate\n"
	@uv run scripts/validate.py

cie11:
	@printf "\n:: copiando base a deis-cie11\n"
	@cp data/final/urgencias_deis_*.parquet deis-cie11/data/raw/urgencias_deis_2019_2025.parquet
	@printf "\n:: deis-cie11 — build\n"
	@cd deis-cie11 && uv run python src/ingestion/master.py
	@cd deis-cie11 && uv run python src/ingestion/resolver.py
	@cd deis-cie11 && uv run python src/ingestion/curator.py

all: build validate cie11

clean:
	@printf "\n:: limpiando archivos generados\n"
	@rm -rf data/utf8_fixed data/final data/reference/*.parquet