COMPOSE_BIN=docker compose
COMPOSE_FILE=deployment/docker-compose.yml
BASE_COMPOSE_COMMAND=$(COMPOSE_BIN) -f $(COMPOSE_FILE) --project-name apt-tracker

run:
	poetry run python -m src.main

deploy-dev: $(COMPOSE_FILE)
	$(BASE_COMPOSE_COMMAND) --profile dev up -d

destroy-dev: $(COMPOSE_FILE)
	$(BASE_COMPOSE_COMMAND) --profile dev down

deploy-prod: $(COMPOSE_FILE)
	$(BASE_COMPOSE_COMMAND) --profile prod up -d

destroy-prod: $(COMPOSE_FILE)
	$(BASE_COMPOSE_COMMAND) --profile prod down
