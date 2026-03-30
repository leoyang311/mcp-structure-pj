.PHONY: install dev-install test clean lint format run-cli run-api check-env docker-up docker-down setup

# ── 安装 ────────────────────────────────────────────────────────────────────────
install:
	uv sync

dev-install:
	uv sync --all-extras

# ── 测试 ────────────────────────────────────────────────────────────────────────
test:
	uv run pytest test_enhanced_anti_censorship.py test_qwen3_three_topics.py -v

# ── 代码质量 ─────────────────────────────────────────────────────────────────────
lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy src/content_factory/

# ── 清理 ────────────────────────────────────────────────────────────────────────
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf .pytest_cache/ dist/ *.egg-info/

# ── 环境检查 ─────────────────────────────────────────────────────────────────────
check-env:
	@echo "Checking environment..."
	@test -f .env || (echo "❌ .env not found — run: cp .env.example .env" && exit 1)
	@grep -q "OPENAI_API_KEY" .env || (echo "❌ OPENAI_API_KEY missing in .env" && exit 1)
	@grep -q "TAVILY_API_KEY" .env || (echo "❌ TAVILY_API_KEY missing in .env" && exit 1)
	@echo "✅ Environment check passed"

# ── Docker ───────────────────────────────────────────────────────────────────────
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# ── 启动服务 ─────────────────────────────────────────────────────────────────────
run-cli:
	uv run python cli.py --help

run-api:
	uv run python api_server.py

run-gui:
	uv run python start_gui_smart.py

# ── 完整开发环境 ──────────────────────────────────────────────────────────────────
setup: check-env dev-install
	@echo "✅ Development environment ready"
