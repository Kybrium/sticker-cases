COMPOSE_FILE=docker-compose.dev.yml

# ---- Common ----
up:
	docker compose -f $(COMPOSE_FILE) up --build

down:
	docker compose -f $(COMPOSE_FILE) down

logs:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=100

ps:
	docker compose -f $(COMPOSE_FILE) ps

restart:
	docker compose -f $(COMPOSE_FILE) restart

# Detect LAN IP (best effort)
lan-ip:
	@ip route get 1 | awk '{print $$7; exit}' || \
	hostname -I | awk '{print $$1}' || \
	echo "Could not detect LAN IP"

up-lan:
	@LAN_IP=$$(ip route get 1 | awk '{print $$7; exit}' || hostname -I | awk '{print $$1}') ; \
	if [ -z "$$LAN_IP" ]; then \
	  echo "Could not detect LAN IP. Run: LAN_IP=192.168.x.x make up-lan"; \
	  exit 1; \
	fi ; \
	echo "Using LAN_IP=$$LAN_IP" ; \
	LAN_IP=$$LAN_IP docker compose -f $(COMPOSE_FILE) up --build

# ---- Backend (Django) ----
migrate:
	docker compose -f $(COMPOSE_FILE) exec backend python manage.py migrate

makemigrations:
	docker compose -f $(COMPOSE_FILE) exec backend python manage.py makemigrations

superuser:
	docker compose -f $(COMPOSE_FILE) exec backend python manage.py createsuperuser

shell:
	docker compose -f $(COMPOSE_FILE) exec backend python manage.py shell

bash-backend:
	docker compose -f $(COMPOSE_FILE) exec backend bash

# ---- Frontend (Next.js) ----
bash-frontend:
	docker compose -f $(COMPOSE_FILE) exec frontend sh

# ---- DB ----
psql:
	docker compose -f $(COMPOSE_FILE) exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB