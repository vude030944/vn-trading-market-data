# ============================================================================
# vn-trading-market-data — orchestrates five independent compose stacks
#
#   make up      bring the whole dev stack up IN DEPENDENCY ORDER
#   make test    run the test suite (no docker, no open market required)
#   make status  what is running and how healthy it is
#   make down    stop everything, KEEP the data
# ============================================================================
SHELL := /bin/bash
ENV   := environment/dev
ING   := src/ingestion
TRF   := src/transform
JAR   := vnmd-transform.jar
# Builds run inside a JDK container, so the host needs no Java. Running as the
# host user keeps build/ deletable; Gradle's cache lives in $(TRF)/.gradle/home.
GRADLE := docker run --rm -u "$$(id -u):$$(id -g)" -v "$(CURDIR)/$(TRF)":/w -w /w \
          -e GRADLE_USER_HOME=/w/.gradle/home eclipse-temurin:21-jdk sh ./gradlew --no-daemon -q
PY    := $(ING)/.venv/bin/python
DATA  ?= /home/vude030944/Data_HDD/vn-trading-market-data/dev

.DEFAULT_GOAL := help
.PHONY: help init up down status logs test lint clean \
        kafka clickhouse flink ingestion observability transform topics reset-data \
        transform-build transform-submit transform-test e2e-up e2e-check e2e-down

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

init: ## Create the shared network and data directories on the HDD (run once)
	@docker network inspect vnmd-dev >/dev/null 2>&1 || docker network create vnmd-dev
	@mkdir -p $(DATA)/{redpanda-0,redpanda-1,redpanda-2,clickhouse/{data,logs},flink/{checkpoints,savepoints,uploads},prometheus,grafana}
	@chmod -R 777 $(DATA) 2>/dev/null || true
	@test -f $(ING)/.env || cp $(ING)/.env.example $(ING)/.env
	@echo "ready. Remember to fill in credentials in $(ING)/.env"

kafka: ## Kafka only
	cd $(ENV)/kafka && docker compose up -d

topics: ## Apply retention settings and create the 5 topics (idempotent)
	cd $(ENV)/kafka && ./bootstrap.sh

clickhouse: ## ClickHouse only
	cd $(ENV)/clickhouse && docker compose up -d

transform: ## Apply the ClickHouse schema the Flink job writes into
	cd $(TRF) && bash ./apply.sh

flink: ## Flink cluster (runs the Kafka -> ClickHouse transform job)
	cd $(ENV)/flink && docker compose up -d

transform-build: ## Build the Flink job jar into environment/dev/flink/jobs
	$(GRADLE) shadowJar
	@mkdir -p $(ENV)/flink/jobs && cp $(TRF)/build/libs/$(JAR) $(ENV)/flink/jobs/$(JAR)

# Cancel-then-run: the job resumes from the offsets committed at its last
# checkpoint, so rows written after that checkpoint are inserted again
# (AT_LEAST_ONCE — see src/transform/README.md).
transform-submit: ## (Re)submit the Flink job
	@for id in $$(docker exec flink-jobmanager flink list -r 2>/dev/null \
	      | awk -F' : ' '/vnmd-transform/ {print $$2}'); do \
	    docker exec flink-jobmanager flink cancel $$id; done
	docker exec flink-jobmanager flink run -d /opt/flink/jobs/$(JAR)

transform-test: ## Unit tests of the Flink job (in docker)
	$(GRADLE) test

E2E := docker compose -f environment/e2e/docker-compose.yml

e2e-up: ## Whole pipeline against the broker simulator (self-contained, <= 20G RAM)
	$(E2E) up -d --build

e2e-check: ## Pause the simulator and verify every frame reached ClickHouse
	$(E2E) run --rm e2e-check

e2e-down: ## Tear the e2e stack down, deleting its volumes
	$(E2E) down -v

ingestion: ## Build and run the 3 ingestion services
	cd $(ING) && docker compose up -d --build

observability: ## OTel + Prometheus + Grafana (optional, +0.8G RAM)
	cd $(ENV)/observability && docker compose up -d

# The order is not arbitrary: Kafka must have its topics before ingestion writes,
# and ClickHouse must have its schema before the Flink job starts inserting.
up: init kafka ## Bring the whole dev stack up in dependency order
	@echo "waiting for Kafka to become healthy..."
	@until [ "$$(docker inspect -f '{{.State.Health.Status}}' redpanda-0 2>/dev/null)" = healthy ]; do sleep 2; done
	@$(MAKE) topics clickhouse
	@echo "waiting for ClickHouse to become healthy..."
	@until [ "$$(docker inspect -f '{{.State.Health.Status}}' clickhouse 2>/dev/null)" = healthy ]; do sleep 2; done
	@$(MAKE) transform flink transform-build
	@echo "waiting for Flink to become healthy..."
	@until [ "$$(docker inspect -f '{{.State.Health.Status}}' flink-jobmanager 2>/dev/null)" = healthy ]; do sleep 2; done
	@$(MAKE) transform-submit ingestion
	@$(MAKE) status

down: ## Stop everything (data survives because bind mounts are used)
	-cd $(ING) && docker compose down
	-cd $(ENV)/observability && docker compose down
	-cd $(ENV)/flink && docker compose down
	-cd $(ENV)/clickhouse && docker compose down
	-cd $(ENV)/kafka && docker compose down

status: ## Containers plus feed health
	@docker ps --format 'table {{.Names}}\t{{.Status}}' | head -20
	@echo
	@docker exec clickhouse clickhouse-client --user vnmd --password vnmd_dev_password \
	   --query 'SELECT * FROM vnmd.v_feed_health FORMAT PrettyCompact' 2>/dev/null \
	   || echo "  (ClickHouse not ready yet)"

logs: ## Tail the 3 ingestion services
	cd $(ING) && docker compose logs -f --tail=50

test: ## Full test suite — runs any time, no docker needed
	$(PY) -m pytest $(ING)/tests -q

lint: ## Check Python, YAML and shell syntax
	@$(PY) -m compileall -q $(ING) && echo "  python OK"
	@python3 -c "import yaml,glob;[yaml.safe_load(open(f)) for f in glob.glob('$(ENV)/*/docker-compose.yml')+glob.glob('$(ING)/docker-compose.yml')+glob.glob('environment/prod/*/docker-compose.yml')];print('  yaml OK')"
	@bash -n $(ENV)/kafka/bootstrap.sh && bash -n $(TRF)/apply.sh && echo "  shell OK"

reset-data: ## DELETE ALL data (credentials are untouched)
	@read -p "Delete everything under $(DATA)? [y/N] " a; [ "$$a" = y ] || exit 1
	$(MAKE) down
	rm -rf $(DATA)/*
	@echo "deleted. Run 'make up' to rebuild"

clean: ## Remove temporary files
	find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
	find . -name .pytest_cache -type d -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(TRF)/build $(TRF)/.gradle
