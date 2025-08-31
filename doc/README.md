# Documentation Index

This directory contains comprehensive documentation for the OFS Mockup Server project.

## Documentation Structure

### 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md)
**System Architecture and Design**
- High-level system overview with Mermaid diagrams
- Component architecture and data flow
- API and authentication architecture
- Multi-language and tax system architecture
- Error handling and testing architecture
- Performance characteristics and deployment patterns

### 🌐 [API.md](API.md)
**Complete REST API Documentation**
- Authentication and endpoint specifications
- Request/response examples with full JSON schemas
- Error handling and status codes
- Tax system and multi-language support
- Integration examples with cURL and Python
- Configuration options and testing scenarios

### 💻 [DEVELOPMENT.md](DEVELOPMENT.md)
**Development Environment and Guidelines**
- Local development setup (standard Python and Nix)
- Project structure and code organization
- Testing strategies (manual, automated, performance)
- Code quality tools and pre-commit hooks
- Debugging and troubleshooting guidance
- Deployment options and contributing guidelines

## Quick Start Guide

### For Developers
1. Read [DEVELOPMENT.md](DEVELOPMENT.md) for setup instructions
2. Review [API.md](API.md) for endpoint specifications
3. Check [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions
4. Use the helper scripts in `../scripts/` for testing

### For Integration Testing
1. Start with [API.md](API.md) for endpoint documentation
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for data flow understanding
3. Use [DEVELOPMENT.md](DEVELOPMENT.md) for deployment options
4. Customize configuration constants for test scenarios

### For System Administrators
1. Begin with [DEVELOPMENT.md](DEVELOPMENT.md) for deployment options
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system understanding
3. Check [API.md](API.md) for integration requirements
4. Use Docker or systemd deployment examples

## Key Features Documented

### 🧾 **Fiscal Device Simulation**
- Complete OFS API implementation
- Realistic invoice processing and receipt generation
- Multi-language support (Bosnian/Serbian Latin/Cyrillic, English)
- Tax system simulation for Bosnia and Herzegovina
- Device status and PIN authentication simulation

### 📊 **Testing Capabilities**
- Configurable device states and error scenarios
- Invoice search and retrieval functionality
- Support for all fiscal operations (normal, refund, copy, advance)
- Multiple payment types and tax categories
- Performance testing and load simulation

### 🔒 **Security Features**
- API key authentication system
- PIN-based security element simulation
- Configurable authorization scenarios
- Error handling with proper HTTP status codes

### 🌍 **Multi-language Support**
- Bosnian (Latin and Cyrillic scripts)
- Serbian (Latin script)
- English
- Configurable language responses
- Realistic localized tax category names

### ⚙️ **Configuration Options**
- Business information customization
- Tax rate and category configuration
- Device status simulation (ready, PIN required, security element missing)
- API key and PIN customization
- Language preference settings

## Technology Stack Covered

- **Backend**: FastAPI with async support
- **Validation**: Pydantic models with type hints
- **Server**: Uvicorn ASGI server
- **Development**: Nix flake for reproducible environments
- **Testing**: pytest, httpx, FastAPI test client
- **Code Quality**: black, isort, flake8, mypy
- **Deployment**: Docker, systemd, direct Python

## Diagram Types Used

The documentation includes various Mermaid diagrams:
- **System Architecture** - High-level component relationships
- **Data Flow** - Sequence diagrams for API interactions
- **Component Architecture** - Module dependency graphs
- **API Architecture** - Endpoint categorization and authentication flow
- **Data Model** - Entity relationship diagrams
- **Multi-language Architecture** - Language support structure

## Configuration Examples

### Basic Server Configuration
```python
API_KEY = "api_key_0123456789abcdef0123456789abcdef"  # Authentication
PIN = "0A10015"                                  # Security PIN
GSC_CODE = "9999"                            # Device status
BUSINESS_NAME = "Your Test Company"          # Company info
SEND_CIRILICA = True                         # Language setting
```

### Test Scenarios
- **Normal Operations** - GSC_CODE = "9999"
- **Security Issues** - GSC_CODE = "1300"  
- **PIN Required** - GSC_CODE = "1500"
- **Error Simulation** - Invoice number "ERROR"

## Usage Examples

### Quick Start
```bash
# Install and run
pip install bringout-ofs-mockup-srv
ofs-mockup-srv

# Or with development setup
git clone https://github.com/bring-out/0.git
cd packages/bringout-ofs-mockup-srv
pip install -e .[dev]
uvicorn ofs_mockup_srv.main:app --reload
```

### Basic Testing
```bash
# Health check
curl http://localhost:8200/

# Process invoice
curl --location 'http://localhost:8200/api/invoices' \
--header 'Authorization: Bearer api_key_0123456789abcdef0123456789abcdef' \
--header 'Content-Type: application/json' \
--data '{"invoiceRequest": {...}}'
```

### Integration Testing
```python
from fastapi.testclient import TestClient
from ofs_mockup_srv.main import app

client = TestClient(app)
response = client.get("/api/status", 
    headers={"Authorization": "Bearer api_key_0123456789abcdef0123456789abcdef"})
assert response.status_code == 200
```

## Maintenance Notes

### Documentation Updates
- Update API.md when adding new endpoints
- Modify ARCHITECTURE.md for design changes
- Update DEVELOPMENT.md for new tools or processes
- Keep configuration examples current with code changes

### Version Synchronization
- Documentation version should match package version
- Update examples when API changes
- Validate all configuration examples
- Test deployment procedures regularly

## Additional Resources

### Project Root Files
- **[../CLAUDE.md](../CLAUDE.md)** - AI context memory for development
- **[../README.md](../README.md)** - Project overview and quick start
- **[../pyproject.toml](../pyproject.toml)** - Package configuration and dependencies

### Code Organization
- **[../ofs_mockup_srv/](../ofs_mockup_srv/)** - Main application code
- **[../scripts/](../scripts/)** - Helper scripts for testing
- **[../patches/](../patches/)** - System patches for Nix environment

### Development Environment
- **[../flake.nix](../flake.nix)** - Nix development environment
- **[../flake.lock](../flake.lock)** - Nix dependency lock file

This documentation provides complete coverage of the OFS Mockup Server, from development setup to production deployment, ensuring successful fiscal integration testing without requiring physical fiscal hardware.