VENV_DIR = .venv

$(VENV_DIR):
	python3 -m venv $(VENV_DIR) && \
	$(VENV_DIR)/bin/pip install --upgrade pip && \
	$(VENV_DIR)/bin/pip install -r requirements.txt

install: $(VENV_DIR)

black: $(VENV_DIR)
	$(VENV_DIR)/bin/black .

ruff: $(VENV_DIR)
	$(VENV_DIR)/bin/ruff check .

pytest: $(VENV_DIR)
	PYTHONPATH=. $(VENV_DIR)/bin/pytest

test: black ruff pytest

#
# Docker commands
#

DOCKER_NETWORK=pizza_bot_network

POSTGRES_VOLUME=postgres_data
POSTGRES_CONTAINER=postgres_17

BOT_IMAGE=ncuxe/unn_pizza_bot
BOT_CONTAINER=pizza_bot

include .env
export $(shell sed 's/=.*//' .env)

docker_volume:
	docker volume create $(POSTGRES_VOLUME) || true

docker_net:
	docker network create $(DOCKER_NETWORK) || true

postgres_run: docker_volume docker_net
	docker run -d \
	  --name $(POSTGRES_CONTAINER) \
	  -e POSTGRES_USER="$(POSTGRES_USER)" \
	  -e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	  -e POSTGRES_DB="$(POSTGRES_DATABASE)" \
	  -p "$(POSTGRES_HOST_PORT):$(POSTGRES_CONTAINER_PORT)" \
	  -v $(POSTGRES_VOLUME):/var/lib/postgresql/data \
	  --network $(DOCKER_NETWORK) \
	  postgres:17

postgres_stop:
	docker stop $(POSTGRES_CONTAINER)
	docker rm $(POSTGRES_CONTAINER)

build:
	docker build \
	  -t $(BOT_IMAGE) \
	  --platform linux/amd64,linux/arm64 \
	  -f Dockerfile \
	  .

push:
	docker push $(BOT_IMAGE)

run: docker_net
	docker run -d \
	  --name $(BOT_CONTAINER) \
	  --restart unless-stopped \
	  -e POSTGRES_HOST="$(POSTGRES_CONTAINER)" \
	  -e POSTGRES_PORT="$(POSTGRES_CONTAINER_PORT)" \
	  -e POSTGRES_USER="$(POSTGRES_USER)" \
	  -e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	  -e POSTGRES_DATABASE="$(POSTGRES_DATABASE)" \
	  -e TELEGRAM_TOKEN="$(TELEGRAM_TOKEN)" \
	  --network $(DOCKER_NETWORK) \
	  $(BOT_IMAGE)

stop:
	docker stop $(BOT_CONTAINER)
	docker rm $(BOT_CONTAINER)
logs:
	docker logs -f $(BOT_CONTAINER)