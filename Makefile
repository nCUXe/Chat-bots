VENV_DIR = .venv
ACTIVATE_VENV := . $(VENV_DIR)/bin/activate

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)
	$(ACTIVATE_VENV) && pip install --upgrade pip
	$(ACTIVATE_VENV) && pip install --requirement requirements.txt

install: $(VENV_DIR)

black: $(VENV_DIR)
	$(ACTIVATE_VENV) && black .

ruff: $(VENV_DIR)
	$(ACTIVATE_VENV) && ruff check .

test: black ruff


DOCKER_NETWORK=aiogram_bot_network

BOT_IMAGE=ncuxe/unn_pizza_bot
BOT_CONTAINER=aiogram_bot

include .env
export $(shell sed 's/=.*//' .env)

docker_net:
	docker network create $(DOCKER_NETWORK) || true

build:
	docker build \
	  -t $(BOT_IMAGE) \
	  --platform linux \
	  -f Dockerfile \
	  .

push:
	docker push $(BOT_IMAGE)

run: docker_net
	docker run -d \
	  --name $(BOT_CONTAINER) \
	  --restart unless-stopped \
	  -e TELEGRAM_TOKEN="$(TELEGRAM_TOKEN)" \
	  --network $(DOCKER_NETWORK) \
	  $(BOT_IMAGE)

stop:
	docker stop $(BOT_CONTAINER)
	docker rm $(BOT_CONTAINER)