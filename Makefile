# OpenGD77 SSRFLite Generator Makefile
# Provides convenient commands for development and documentation

.PHONY: help install test docs docs-profiles docs-policies docs-ssrf schema stamp-headers validate-schema clean lint format

# Default target
help: ## Show this help message
	@echo "OpenGD77 SSRFLite Generator - Development Commands"
	@echo "================================================="
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	uv sync

test: ## Run tests
	uv run python -m pytest tests/

docs: ## Generate all documentation
	@echo "📚 Generating all documentation..."
	./update-docs.sh

docs-profiles: ## Generate profile documentation only
	@echo "📋 Generating profile documentation..."
	uv run python generate_profile_docs.py

docs-policies: ## Generate policy documentation only  
	@echo "⚙️ Generating policy documentation..."
	uv run python generate_policy_docs.py

docs-ssrf: ## Generate SSRF documentation only
	@echo "📡 Generating SSRF documentation..."
	uv run python generate_ssrf_docs.py

schema: ## Regenerate the versioned SSRF-Lite JSON Schema from the models
	@echo "🧬 Generating SSRF-Lite JSON Schema..."
	uv run python generate_ssrf_schema.py

stamp-headers: ## Stamp $$schema + ssrf_lite_version headers onto SSRF-Lite YAML
	@echo "🏷️  Stamping SSRF-Lite schema headers..."
	uv run python stamp_ssrf_headers.py

validate-schema: ## Verify the committed schema and YAML headers are up to date
	@echo "🔍 Validating SSRF-Lite schema and headers..."
	uv run python generate_ssrf_schema.py --check
	uv run python stamp_ssrf_headers.py --check

generate: ## Generate OpenGD77 CSV files (default profile)
	uv run python generate_opengd_import.py

generate-profile: ## Generate CSV files for specific profile (e.g., make generate-profile PROFILE=chicago_amateur)
	uv run python generate_opengd_import.py --profile $(or $(PROFILE),chicago_amateur)

generate-n76: ## Generate VGC N76 CSV files (default profile)
	uv run python generate_n76_import.py

generate-n76-profile: ## Generate N76 CSV for specific profile (e.g., make generate-n76-profile PROFILE=gmrs_only)
	uv run python generate_n76_import.py --profile $(or $(PROFILE),gmrs_only)

generate-chirp: ## Generate CHIRP CSV files (default profile)
	uv run python generate_chirp_csv.py

generate-chirp-profile: ## Generate CHIRP CSV for specific profile (e.g., make generate-chirp-profile PROFILE=chicago_amateur)
	uv run python generate_chirp_csv.py --profile $(or $(PROFILE),chicago_amateur)

list-profiles: ## List all available profiles
	uv run python generate_opengd_import.py --list-profiles

list-policies: ## List all available policy files
	uv run python generate_policy_docs.py --list-files

list-ssrf: ## List all available SSRF files
	uv run python generate_ssrf_docs.py --list-files

lint: ## Run linting checks
	@echo "🔍 Running linting checks..."
	@if command -v ruff >/dev/null 2>&1; then \
		uv run ruff check .; \
	else \
		echo "⚠️  ruff not available, skipping lint"; \
	fi

format: ## Format code
	@echo "🎨 Formatting code..."
	@if command -v ruff >/dev/null 2>&1; then \
		uv run ruff format .; \
	else \
		echo "⚠️  ruff not available, skipping format"; \
	fi

clean: ## Clean generated files
	@echo "🧹 Cleaning generated files..."
	rm -rf opengd77_cps_import_generated/
	rm -rf dm32_cps_import_generated/
	rm -rf n76_import_generated/
	rm -rf chirp_import_generated/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-docs: ## Clean generated documentation
	@echo "🧹 Cleaning documentation files..."
	rm -rf docs/profiles/*.md docs/policies/*.md docs/ssrf/*.md

validate-docs: ## Validate that documentation is up to date
	@echo "🔍 Validating documentation..."
	@./update-docs.sh > /tmp/docs_output 2>&1
	@if git diff --quiet docs/; then \
		echo "✅ Documentation is up to date"; \
	else \
		echo "❌ Documentation is out of date. Run 'make docs' to update."; \
		git diff --stat docs/; \
		exit 1; \
	fi

setup-hooks: ## Install git hooks for automatic documentation updates
	@echo "🪝 Setting up git hooks..."
	@if [ -f .git/hooks/pre-commit ]; then \
		echo "✅ Pre-commit hook already exists"; \
	else \
		echo "❌ Pre-commit hook not found. Please run this from the project root."; \
		exit 1; \
	fi
	@chmod +x .git/hooks/pre-commit
	@echo "✅ Git hooks configured"

dev-setup: install setup-hooks docs ## Full development setup
	@echo "🚀 Development setup complete!"
	@echo
	@echo "Available commands:"
	@echo "  make docs          - Generate all documentation" 
	@echo "  make generate      - Generate OpenGD77 CSV files"
	@echo "  make test          - Run tests"
	@echo "  make list-profiles - See available profiles"
	@echo
	@echo "Documentation will auto-update on git commits."

status: ## Show project status
	@echo "📊 OpenGD77 SSRFLite Generator Status"
	@echo "======================================"
	@echo
	@echo "📁 Source Files:"
	@printf "   Profiles: %d files\n" $$(ls profiles/*.yml 2>/dev/null | wc -l)
	@printf "   Policies: %d files\n" $$(ls policies/*.yml 2>/dev/null | wc -l)
	@printf "   SSRF:     %d files\n" $$(find ssrf -name "*.yml" ! -name "_*" 2>/dev/null | wc -l)
	@echo
	@echo "📚 Documentation:"
	@printf "   Profile docs: %d files\n" $$(ls docs/profiles/*.md 2>/dev/null | grep -v README.md | wc -l)
	@printf "   Policy docs:  %d files\n" $$(ls docs/policies/*.md 2>/dev/null | grep -v README.md | wc -l)
	@printf "   SSRF docs:    %d files\n" $$(ls docs/ssrf/*.md 2>/dev/null | grep -v README.md | wc -l)
	@echo
	@echo "🔧 Git Hooks:"
	@if [ -x .git/hooks/pre-commit ]; then \
		echo "   ✅ Pre-commit hook: Active"; \
	else \
		echo "   ❌ Pre-commit hook: Not found/executable"; \
	fi