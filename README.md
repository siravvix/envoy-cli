# envoy-cli

A lightweight CLI for managing and syncing `.env` files across environments with encryption support.

---

## Installation

```bash
pip install envoy-cli
```

Or with pipx for isolated installs:

```bash
pipx install envoy-cli
```

---

## Usage

```bash
# Initialize envoy in your project
envoy init

# Push your local .env to a remote environment
envoy push --env production

# Pull and decrypt the latest .env from staging
envoy pull --env staging

# Encrypt your .env file locally
envoy encrypt --key my-secret-key

# List all tracked environments
envoy list
```

> **Note:** Store your encryption key securely and never commit it to version control.

---

## Features

- 🔐 AES encryption for `.env` files
- 🔄 Sync across multiple environments (dev, staging, production)
- ⚡ Lightweight with minimal dependencies
- 🛠️ Simple, intuitive CLI commands

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the [MIT License](LICENSE).