# File Convert MCP Server
[![smithery badge](https://smithery.ai/badge/@convertguru/file-convert-mcp)](https://smithery.ai/server/@convertguru/file-convert-mcp)

A Model Context Protocol (MCP) server for converting files between various formats.

File Convert is an MCP server designed to handle the conversion of a wide array of file formats, including images, office documents, audio, video, text, and data files. It aims to provide seamless transformation into popular formats such as PDF, JPG, MP4, and HTML, among others. This server offers a set of powerful tools to convert diverse file types into easily accessible and widely compatible formats like PDF, JPG, PNG, TXT.

## ✨ Features

- **Intelligent File Type Detection:** Employs a combination of AI, TrID, and magic bytes for accurate file type identification.
- **Versatile File Conversion:** Supports conversion between numerous file types and the following popular formats:
    - **Images:** Handles a vast range of formats, including many legacy ones. Converts to PDF, JPG, PNG.
    - **Office Documents:** Converts to PDF, TXT, HTML.
    - **Audio/Video:** Converts to MP3, MP4.
    - **Databases:** Converts to CSV.
    - **Various Files:** Offers conversion capabilities for other file types as well.

## 🛠️ Requirements

1. **Python:** Version 3.12 or higher is required.
2. **uv Tool:** Install the [Python uv tool](https://docs.astral.sh/uv/getting-started/installation/) for efficient dependency management and easy execution of the MCP server.
3. **API Key (Development):** As of May 2025, the MCP is in its testing phase, and **no API key is currently required** for development. For future production use, please [contact the Convert.Guru team](https://convert.guru/contact) to obtain an API key.

## 🚀 Usage with Desktop App

To integrate this server with your desktop application, add the following configuration to your app's server settings. If necessary, adjust the absolute path to the `uv`/`uvx` executables (or `uv.exe`/`uvx.exe` on Windows).

**Using `uvx` (recommended):**

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
```

**5. Modify the server logic if needed:**
Edit the main server file located at `src/file_convert_mcp/server.py.`

**6. Clearing the `uv` Cache (if needed):**
If `uv` has cached an older version of the code in `~/.cache/uv`, you might need to clear the cache. Alternatively, use `uv` with the `-n` or `--no-cache` option to bypass it.

## ⚙️ Available Tools

The MCP server provides the following tools:

* `detect_file_type`: Analyzes the first 200 bytes of an uploaded file and uses the Convert.Guru API to determine its type.
* `convert_file`: Converts a given file to a specified output format. The desired file extension should be passed as the `ext_out` parameter.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for complete details.