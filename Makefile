# TransTube Build System
# Builds standalone apps for macOS ARM64 and Windows

# Detect OS
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

# App metadata
APP_NAME = TransTube
APP_VERSION = 1.0.0
BUNDLE_ID = com.transtube.app

# Directories
BUILD_DIR = build
DIST_DIR = dist
PYTHON_BUNDLE_DIR = $(BUILD_DIR)/python_bundle
FLUTTER_DIR = transtube_gui
CONFIG_DIR = config
BUILD_SCRIPTS_DIR = build_scripts

# Python configuration
PYTHON = python3
PIP = pip3
PYINSTALLER = pyinstaller

# Platform-specific settings
ifeq ($(UNAME_S),Darwin)
	PLATFORM = macos
	FLUTTER_BUILD_CMD = flutter build macos --release
	APP_OUTPUT = $(FLUTTER_DIR)/build/macos/Build/Products/Release/$(APP_NAME).app
	DIST_OUTPUT = $(DIST_DIR)/$(APP_NAME)-macOS-arm64.app
else ifeq ($(OS),Windows_NT)
	PLATFORM = windows
	FLUTTER_BUILD_CMD = flutter build windows --release
	APP_OUTPUT = $(FLUTTER_DIR)/build/windows/x64/runner/Release
	DIST_OUTPUT = $(DIST_DIR)/$(APP_NAME)-Windows.exe
else
	$(error Unsupported platform: $(UNAME_S))
endif

# Default target
.PHONY: all
all: build

# Install all dependencies
.PHONY: deps
deps: deps-python deps-flutter

.PHONY: deps-python
deps-python:
	@echo "Installing Python dependencies..."
	$(PIP) install -r requirements.txt
	$(PIP) install pyinstaller
	@echo "Downloading spaCy model..."
	$(PYTHON) -m spacy download en_core_web_sm || true

.PHONY: deps-flutter
deps-flutter:
	@echo "Installing Flutter dependencies..."
	cd $(FLUTTER_DIR) && flutter pub get

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -rf $(DIST_DIR)
	rm -rf $(FLUTTER_DIR)/build
	rm -rf dist
	rm -rf build
	rm -rf *.spec
	find . -name "__pycache__" -type d -exec rm -rf {} + || true
	find . -name "*.pyc" -delete || true

# Build for current platform
.PHONY: build
build: clean deps
ifeq ($(PLATFORM),macos)
	@$(MAKE) build-macos
else ifeq ($(PLATFORM),windows)
	@$(MAKE) build-windows
endif

# Build for macOS ARM64
.PHONY: build-macos
build-macos: bundle-python-macos
	@echo "Building Flutter app for macOS..."
	cd $(FLUTTER_DIR) && flutter clean
	cd $(FLUTTER_DIR) && $(FLUTTER_BUILD_CMD)
	
	@echo "Preparing distribution..."
	mkdir -p $(DIST_DIR)
	cp -R $(APP_OUTPUT) $(DIST_OUTPUT)
	
	@echo "Embedding Python backend..."
	mkdir -p "$(DIST_OUTPUT)/Contents/Resources/backend"
	cp -R $(PYTHON_BUNDLE_DIR)/dist/transtube_backend/* "$(DIST_OUTPUT)/Contents/Resources/backend/"
	
	@echo "Setting permissions..."
	chmod +x "$(DIST_OUTPUT)/Contents/MacOS/transtube_gui"
	find "$(DIST_OUTPUT)/Contents/Resources/backend" -name "*.dylib" -o -name "*.so" -exec chmod +x {} \;
	
	@echo "Code signing (ad-hoc)..."
	codesign --force --deep --sign - "$(DIST_OUTPUT)"
	
	@echo "Build complete: $(DIST_OUTPUT)"

# Build for Windows
.PHONY: build-windows
build-windows: bundle-python-windows
	@echo "Building Flutter app for Windows..."
	cd $(FLUTTER_DIR) && flutter clean
	cd $(FLUTTER_DIR) && $(FLUTTER_BUILD_CMD)
	
	@echo "Preparing distribution..."
	mkdir -p $(DIST_DIR)/$(APP_NAME)-Windows
	cp -R $(APP_OUTPUT)/* $(DIST_DIR)/$(APP_NAME)-Windows/
	
	@echo "Embedding Python backend..."
	mkdir -p $(DIST_DIR)/$(APP_NAME)-Windows/backend
	cp -R $(PYTHON_BUNDLE_DIR)/dist/transtube_backend/* $(DIST_DIR)/$(APP_NAME)-Windows/backend/
	
	@echo "Creating portable package..."
	cd $(DIST_DIR) && zip -r $(APP_NAME)-Windows-Portable.zip $(APP_NAME)-Windows
	
	@echo "Build complete: $(DIST_DIR)/$(APP_NAME)-Windows-Portable.zip"

# Bundle Python backend for macOS
.PHONY: bundle-python-macos
bundle-python-macos:
	@echo "Creating build directories..."
	mkdir -p $(BUILD_DIR) $(CONFIG_DIR) $(BUILD_SCRIPTS_DIR)
	
	@echo "Creating Python bundling script..."
	@$(MAKE) create-bundle-script
	
	@echo "Creating PyInstaller spec for macOS..."
	@$(MAKE) create-pyinstaller-spec-macos
	
	@echo "Bundling Python backend for macOS..."
	cd $(BUILD_DIR) && $(PYINSTALLER) ../$(CONFIG_DIR)/pyinstaller_macos.spec --clean --noconfirm

# Bundle Python backend for Windows
.PHONY: bundle-python-windows
bundle-python-windows:
	@echo "Creating build directories..."
	mkdir -p $(BUILD_DIR) $(CONFIG_DIR) $(BUILD_SCRIPTS_DIR)
	
	@echo "Creating Python bundling script..."
	@$(MAKE) create-bundle-script
	
	@echo "Creating PyInstaller spec for Windows..."
	@$(MAKE) create-pyinstaller-spec-windows
	
	@echo "Bundling Python backend for Windows..."
	cd $(BUILD_DIR) && $(PYINSTALLER) ../$(CONFIG_DIR)/pyinstaller_windows.spec --clean --noconfirm

# Create Python bundling script
.PHONY: create-bundle-script
create-bundle-script:
	$(PYTHON) -c "from build_scripts.create_bundle_script import create_script; create_script()" || \
	@echo "Creating bundling script..."

# Create PyInstaller spec for macOS
.PHONY: create-pyinstaller-spec-macos
create-pyinstaller-spec-macos:
	$(PYTHON) -c "from build_scripts.create_pyinstaller_specs import create_macos_spec; create_macos_spec()" || \
	@echo "Creating macOS spec file..."

# Create PyInstaller spec for Windows
.PHONY: create-pyinstaller-spec-windows
create-pyinstaller-spec-windows:
	$(PYTHON) -c "from build_scripts.create_pyinstaller_specs import create_windows_spec; create_windows_spec()" || \
	@echo "Creating Windows spec file..."

# Development build (with mock service)
.PHONY: dev
dev:
	cd $(FLUTTER_DIR) && flutter run -d chrome

# Run tests
.PHONY: test
test:
	cd $(FLUTTER_DIR) && flutter test
	$(PYTHON) -m pytest tests/ || true

# Help
.PHONY: help
help:
	@echo "TransTube Build System"
	@echo ""
	@echo "Usage:"
	@echo "  make build          - Build for current platform"
	@echo "  make build-macos    - Build for macOS ARM64"
	@echo "  make build-windows  - Build for Windows"
	@echo "  make deps           - Install all dependencies"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make dev            - Run in development mode"
	@echo "  make test           - Run tests"
	@echo "  make help           - Show this help message"
	@echo ""
	@echo "Platform: $(PLATFORM)"
	@echo "Architecture: $(UNAME_M)"