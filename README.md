# File Convert MCP Server
A Model Context Protocol (MCP) server for converting files between different formats

File Convert is a Model Context Protocol (MCP) server that can convert a lot of different file formats (images/office documents/audio/video/text/data/...) intothe  most popular formats like PDF/JPG/MP4/HTML and others. It provides a set of tools to transform Office documents, images, audio and video files and more into easily readable formats like PDF/JPG/PNG/TXT.

## Features

- Detect file type with AI + Trid + magic
- Convert multiple file types to PDF/JPG/PNG/MP3/MP4/TXT/HTML/CSV:
  - Images (supports A LOT of legacy formats)
  - Office Documets
  - Audio/Video
  - Databases
  - Various files

## Requirements

1. Python >= 3.12
2. <a href="https://docs.astral.sh/uv/getting-started/installation/">Python uv tool</a> for resolving python dependencies and running MCP easily

## Usage with Desktop App

To integrate this server with a desktop app, add the following to your app's server configuration. If needed - set the absolute path to uv/uvx or uv.exe/uvx.exe on Windows:

```js
{
  "mcpServers": {
    "file-convert-mcp": {
      "command": "/home/User/.local/bin/uvx",
      "args": ["--from", "git+https://github.com/convertguru/file-convert-mcp.git", "file-convert-mcp"],
      "env": {
        "CONVERT_GURU_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Or if you cloned the repo to the folder on your disk:

```js
{
  "mcpServers": {
    "file-convert-mcp": {
      "command": "/home/User/.local/bin/uv",
      "args": ["--directory", "/home/User/file-convert-mcp/src/file_convert_mcp", "run", "server.py"],
      "env": {
        "CONVERT_GURU_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Or using uvx from disk:

```js
{
  "mcpServers": {
    "file-convert-mcp": {
      "command": "uvx",
      "args": ["--from", "/home/User/file-convert-mcp", "file-convert-mcp"],
      "env": {
        "CONVERT_GURU_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Development

1. Clone this repository
```
git clone https://github.com/convertguru/file-convert-mcp.git
```

2. Fetch and cache python dependencies (optional, uvx does it automagically)
```
cd file-convert-mcp
uv sync
cd ..
```

3. Run MCP server locally
```
uvx --from ./file-convert-mcp file-convert-mcp

## OR
uv run file-convert-mcp/src/file_convert_mcp/server.py

## OR
uv --directory file-convert-mcp/src/file_convert_mcp run server.py

## OR
cd file-convert-mcp/src/file_convert_mcp
uv run server.py

## OR via uvx from github
uvx --from git+https://github.com/convertguru/file-convert-mcp.git file-convert-mcp

```

4. Edit `src/file_convert_mcp/server.py` if needed


## Available Tools

- `detect_file_type`: Detect file type by uploading first 200 bytes of a file to Convert.Guru API
- `convert_file`: Convert a file into another format. Pass the desired extension (`ext_out`)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
