.PHONY: install dev build test clean docker-up docker-down

# Install all dependencies
install:
	pip install -r requirements.txt
	cd dashboard_v1 && npm install

# Run development servers
dev:
	@echo "Starting API server..."
	python api.py &
	@echo "Starting Dashboard..."
	cd dashboard_v1 && npm run dev

# Build for production
build:
	cd dashboard_v1 && npm run build

# Run tests
test:
	pytest tests/ -v --cov=.

# Clean generated files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true

# Docker commands
docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

# Database reset
db-reset:
	rm -f apex.db
	python -c "from api import init_db; init_db()"

# Quick commit
commit:
	git add -A
	git commit -m "$(msg)"

# Format code
format:
	cd dashboard_v1 && npm run format
