# YouTube Subtitle API Makefile

.PHONY: help install dev test build run clean kill-port

help:
	@echo "YouTube Subtitle API - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install         - Install dependencies (including test deps)"
	@echo ""
	@echo "Development:"
	@echo "  dev             - Start dev server with auto-reload"
	@echo "  kill-port       - Kill process on port 10000"
	@echo ""
	@echo "Testing:"
	@echo "  test            - Run all tests"
	@echo "  test-v          - Run all tests (verbose)"
	@echo ""
	@echo "Docker:"
	@echo "  build           - Build Docker image"
	@echo "  run             - Run Docker container"
	@echo ""
	@echo "Utilities:"
	@echo "  clean           - Remove cache and temp files"

install:
	pip install -r requirements-dev.txt

dev: kill-port
	uvicorn app.main:app --host 0.0.0.0 --port 10000 --reload

test:
	python3 -m pytest tests/

test-v:
	python3 -m pytest tests/ -v

build:
	docker build -t yt-api .

run:
	docker run -p 10000:10000 yt-api

kill-port:
	@fuser -k 10000/tcp 2>/dev/null || echo "Port 10000 is free"

clean:
	rm -rf __pycache__ app/__pycache__ tests/__pycache__ .pytest_cache
