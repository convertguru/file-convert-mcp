# File Convert MCP Server
[![PyPI version](https://img.shields.io/pypi/v/file-convert-mcp.svg)](https://pypi.org/project/file-convert-mcp/)
[![smithery badge](https://smithery.ai/badge/@convertguru/file-convert-mcp)](https://smithery.ai/server/@convertguru/file-convert-mcp)

A Model Context Protocol (MCP) server for converting files between various formats.

File Convert is an MCP server designed to handle the conversion of a wide array of file formats, including images, office documents, audio, video, text, and data files. It aims to provide seamless transformation into popular formats such as PDF, JPG, MP4, and HTML, among others. This server offers a set of powerful tools to convert diverse file types into easily accessible and widely compatible formats like PDF, JPG, PNG, TXT.

> **Using an autonomous HTTP/x402/MPP agent instead of MCP?** Check out the pay-per-request [Convert.Guru x402 & MPP API](https://convert.guru/api/x402/v1/) (250+ formats, Base USDC / Tempo PATHUSD).

## ✨ Features

- **Intelligent File Type Detection:** Employs a combination of AI, TrID, and magic bytes for accurate file type identification.
- **Versatile File Conversion:** Supports conversion between numerous file types and the following popular formats:
    - **Images:** Handles a vast range of formats, including many legacy ones. Converts to PDF, JPG, PNG.
    - **Office Documents:** Converts to PDF, TXT, HTML.
    - **Audio/Video:** Converts to MP3, MP4.
    - **Databases:** Converts to CSV.
    - **Various Files:** Offers conversion capabilities for other file types as well.

## 🛠️ Requirements

1. **Python:** Version 3.10 or higher is required.
2. **uv Tool:** Install the [Python uv tool](https://docs.astral.sh/uv/getting-started/installation/) for efficient dependency management and easy execution of the MCP server.
3. **API Key (Development):** The MCP is free to test during development, and **no API key is currently required**. For high-volume production use, please [contact the Convert.Guru team](https://convert.guru/contact) to obtain an API key.

## 🚀 Usage with Desktop App (Claude Desktop, Cursor, Windsurf)

To integrate this server with your desktop application, add the following configuration to your app's server settings. If necessary, adjust the absolute path to the `uv`/`uvx` executables (or `uv.exe`/`uvx.exe` on Windows).

**Using `uvx` from PyPI (recommended):**

```json
{
  "mcpServers": {
    "file-convert": {
      "command": "uvx",
      "args": ["file-convert-mcp"]
    }
  }
}
```

**Or using `uvx` directly from GitHub:**

```json
{
  "mcpServers": {
    "file-convert": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/convertguru/file-convert-mcp.git", "file-convert-mcp"],
      "env": {
        "CONVERT_GURU_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**If you have cloned the repository locally (adjust paths as needed):**

```json
{
  "mcpServers": {
    "file-convert": {
      "command": "/home/User/.local/bin/uv",
      "args": ["--directory", "/home/User/file-convert-mcp/src/file_convert_mcp", "run", "server.py"],
      "env": {
        "CONVERT_GURU_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Using local `uvx`:**

```json
{
  "mcpServers": {
    "file-convert": {
      "command": "uvx",
      "args": ["--from", "/home/User/file-convert-mcp", "file-convert-mcp"],
      "env": {
        "CONVERT_GURU_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Environment Variables

The MCP server supports the following environment variables:

- **`CONVERT_GURU_API_KEY`**: Your Convert.Guru API key (optional for development)
- **`TRANSPORT`**: Transport method for the MCP server
  - `"stdio"` (default): Standard input/output transport
  - `"http"`: HTTP transport (streamable) with REST API endpoints
- **`PORT`**: Port number for HTTP transport (default: 8000, only used when `TRANSPORT=http`)

When using HTTP transport, the server provides additional endpoints:
- `GET /health` - Health check endpoint
- `GET /tools` - List of available MCP tools

Also, see this guide on how to [set up MCP tools in Claude Desktop](https://modelcontextprotocol.io/quickstart/user#for-claude-desktop-users).

### Installing via Smithery

To install file-convert-mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@convertguru/file-convert-mcp):

```bash
npx -y @smithery/cli install @convertguru/file-convert-mcp --client claude
```

## 🛠️ Development

Get started with local development by following these steps:

**1. Clone the repository:**

```bash
git clone https://github.com/convertguru/file-convert-mcp.git
```

**2. Fetch and cache Python dependencies (optional, `uvx` handles this automatically):**

```bash
cd file-convert-mcp
uv sync
cd ..
```

**3. Create .env file with your (optional for now) API key:**

```bash
echo "CONVERT_GURU_API_KEY=your_api_key_here" > file-convert-mcp/.env
```

**4. Run the MCP server locally using various `uv` commands:**

```bash
# Using uvx with .env file from the local directory
cd file-convert-mcp
UV_ENV_FILE=.env uvx --from ./file-convert-mcp file-convert-mcp

# OR using uv directly to run the server script
uv run file-convert-mcp/src/file_convert_mcp/server.py

# OR specifying the directory for uv
uv --directory file-convert-mcp/src/file_convert_mcp run server.py

# OR navigating into the server directory
cd file-convert-mcp/src/file_convert_mcp
uv run server.py

# OR using uvx to fetch the core from the GitHub repository + local .env file
UV_ENV_FILE=.env uvx --from git+https://github.com/convertguru/file-convert-mcp.git file-convert-mcp

# OR run with HTTP transport on custom port
TRANSPORT=http PORT=9000 uv run file-convert-mcp/src/file_convert_mcp/server.py

# OR run with stdio transport (default)
TRANSPORT=stdio uv run file-convert-mcp/src/file_convert_mcp/server.py
```

**5. Create .env file with your configuration (optional for now):**

```bash
# Basic configuration
echo "CONVERT_GURU_API_KEY=your_api_key_here" > file-convert-mcp/.env

# OR with transport configuration
echo "CONVERT_GURU_API_KEY=your_api_key_here" > file-convert-mcp/.env
echo "TRANSPORT=http" >> file-convert-mcp/.env
echo "PORT=8000" >> file-convert-mcp/.env
```

**6. Modify the server logic if needed:**
Edit the main server file located at `src/file_convert_mcp/server.py.`

**7. Clearing the `uv` Cache (if needed):**
If `uv` has cached an older version of the code in `~/.cache/uv`, you might need to clear the cache. Alternatively, use `uv` with the `-n` or `--no-cache` option to bypass it.

## ⚙️ Available Tools

The MCP server provides the following tools:

* `detect_file_type`: Analyzes the first 200 bytes of an uploaded file and uses the Convert.Guru API to determine its type.
* `convert_file`: Converts a given file to a specified output format. The desired file extension should be passed as the `ext_out` parameter.

Files larger than 40 MiB are rejected before upload. All result files are saved
beside the input file. Existing files are preserved by adding numbered suffixes.
The result contains `converted_file_paths` for all downloaded files and retains
`converted_file_path` for the first file for compatibility. If a later download
fails, the error response includes the paths already downloaded.

### Local development and checks (shared user installation)

```powershell
python -m pip install --user pytest build hatchling editables
python -m pip install --user --no-build-isolation -e .
python -m pytest -q
python -m build --no-isolation
```

These tests use a local API substitute and do not upload files to Convert.Guru.
They cover the 40 MiB boundary, multiple results, existing files, partial failure,
native file detection, and the installed STDIO/HTTP command. Large temporary test
files are removed automatically. Building creates local artifacts in `dist/`;
it does not publish them.

On Windows, the package uses `python-magic-bin`, which bundles libmagic.
FastMCP is constrained to the tested 2.x API. If the user Scripts directory is not
on PATH, launch `file-convert-mcp.exe` using its full path, or run
`python -m file_convert_mcp.server`.

## 📜 License

Visit us [https://convert.guru](https://convert.guru/)

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for complete details.
