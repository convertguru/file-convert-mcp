import os
import io
import re
import magic
import json
from typing import Dict, Any
from fastmcp import FastMCP
from dotenv import load_dotenv
import aiohttp
from starlette.responses import JSONResponse
import asyncio

# Load environment variables
load_dotenv()

# Initialize FastMCP
mcp = FastMCP("file-convert-mcp")
base_url = 'https://convert.guru'
api_key = os.getenv("CONVERT_GURU_API_KEY")
if api_key is None:
    api_key = ''

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "mcp-server"})

@mcp.custom_route("/tools", methods=["GET"])
async def list_tools(request):
    tools_info = []
    for tool_name, tool_func in mcp.tools.items():
        tools_info.append({
            "name": tool_name,
            "description": tool_func.__doc__ or "No description available",
            "async": asyncio.iscoroutinefunction(tool_func)
        })
    
    return JSONResponse({
        "tools": tools_info,
        "total_tools": len(tools_info)
    })

@mcp.tool()
async def detect_file_type(file_path: str) -> Dict[str, Any]:
    """Detect file type by sending the first 200 bytes of the file to Convert.Guru API."""
    if not file_path:
        return {"error": "file_path parameter is required"}

    if not os.path.exists(file_path):
        return {"error": f"File not found (use the absolute file path): {file_path}"}

    if not os.path.isfile(file_path):
        return {"error": f"Not a file: {file_path}"}

    try:
        with open(file_path, "rb") as f:
            first_200_bytes = f.read(200)  # Read only the first 200 bytes

        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lstrip('.') # Remove dot
        filename = os.path.basename(file_path)
        file_size_bytes = os.path.getsize(file_path)
        size_hex = hex(file_size_bytes)
        mime_type = magic.Magic(mime=True).from_file(file_path)

        data = [file_extension,size_hex,mime_type,filename]
        separator = '\xFE'
        joined_data = separator.join(data)
        headers = {'cache-control': 'no-cache', 'api-key': api_key}

        data_array = bytearray()
        for char in joined_data:
            data_array.append(ord(char) & 0xFF)

        data_array.append(0xFE)
        data_array.extend(first_200_bytes)

        async with aiohttp.ClientSession() as session:
            async with session.post(base_url + '/api/v1/detect_file_type', data=data_array, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    comment_pattern = re.compile(r'<!--.+-->')
                    # Remove all occurrences of the pattern from the string
                    content = comment_pattern.sub('', content)
                    return {"result": {"file_type_description": content.strip()}}
                else:
                    error_text = await response.text()
                    return {"error": f"API request failed with status {response.status}: {error_text}"}

    except aiohttp.ClientError as e:
        return {"error": f"Error making API request: {e}"}
    except Exception as e:
        return {"error": f"Error processing file: {e}"}

@mcp.tool()
async def convert_file(file_path: str, ext_out: str) -> Dict[str, Any]:
    """Convert a file to other format via Convert.Guru API. Pass the file path and output extension."""
    if not file_path:
        return {"error": "file_path parameter is required"}

    if not ext_out:
        return {"error": "ext_out parameter is required"}

    if not os.path.exists(file_path):
        return {"error": f"File not found (use the absolute file path): {file_path}"}

    if not os.path.isfile(file_path):
        return {"error": f"Not a file: {file_path}"}

    try:
        with open(file_path, "rb") as f:
            chunk = f.read(40*1024*1024)

            filename = os.path.basename(file_path)

            data = aiohttp.FormData()
            data.add_field('file', chunk, filename=filename)
            headers = {'cache-control': 'no-cache', 'api-key': api_key}

            async with aiohttp.ClientSession() as session:
                async with session.post(base_url + '/api/v1/upload', data=data, headers=headers) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        try:
                            # Explicitly parse using json.loads
                            json_result = json.loads(response_text)
                            json_payload = {
                                "filename": json_result['Filename'], "ext_out": ext_out.lower()}
                            conv_response_text = await post_json(base_url + '/api/v1/convert', json_payload, headers)
                            try:
                                # Explicitly parse using json.loads
                                conv_json_result = json.loads(
                                    conv_response_text)
                                
                                ## check for error in conv_json_result
                                if conv_json_result.get('error'):
                                    conv_json_result['error'] = f"File conversion failed: {conv_json_result.get('error')}"
                                    return conv_json_result

                                file_info = conv_json_result.get('file')
                                if file_info and 'ext_out' in file_info and 'urls' in file_info and file_info['urls']:
                                    file_url_path = file_info['urls'][0]
                                    file_extension = file_info.get('ext_out')

                                    if file_url_path.startswith('/'):
                                        full_file_url = base_url + file_url_path
                                    else:
                                        full_file_url = file_url_path

                                    save_path = file_path + '.converted' + \
                                        f".{file_extension}"

                                    download_result = await download_file(session, full_file_url, save_path)
                                    return download_result

                                else:
                                    return {"error": f"File URL information not found in the API response.: {conv_response_text}"}
                            except json.JSONDecodeError:
                                # If the response is not JSON (convert)
                                return {"error": f"API convert request failed - response text is not JSON: {conv_response_text}"}

                        except json.JSONDecodeError:
                            # If the response is not JSON (upload)
                            return {"error": f"API upload request failed - response text is not JSON: {response_text}"}
                    else:
                        error_text = await response.text()
                        return {"error": f"API request failed with status {response.status}: {error_text}"}

    except aiohttp.ClientError as e:
        return {"error": f"Error making API request: {e}"}
    except Exception as e:
        return {"error": f"Error processing file: {e}"}

async def post_json(url: str, data: dict, headers):
    """
    Posts JSON data to a specified URL using aiohttp.

    Args:
        url: The URL to post the JSON data to.
        data: A Python dictionary that will be converted to JSON.
    """
    cloned_headers = headers.copy()
    cloned_headers['Content-Type'] = 'application/json'
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=cloned_headers) as response:
                response_text = await response.text()
                status = response.status
                err = {}

                if status == 200 or status == 400:
                    return response_text
                elif status == 524:
                    err = {"error": f"Error HTTP 524 - operation takes too long to complete, timeout occured."}
                elif status == 500:
                    err = {"error": f"Error HTTP 500 - operation takes too long to complete, internal server error."}
                else:
                    err = {"error": f"Error HTTP {status})."}
                
                return json.dumps(err)
        except aiohttp.ClientError as e:
            err = {"error": f"An error occurred during the request (exception): {e}"}
            return json.dumps(err)

async def download_file(session: aiohttp.ClientSession, url: str, save_path: str) -> Dict[str, Any]:
    """Downloads a file from a URL and saves it to the specified path."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                with open(save_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                return {"result": {"converted_file_path": save_path}}
            else:
                response_text = await response.text()
                return {"error": f"File download from {url} failed with status {response.status}: {response_text}"}
    except aiohttp.ClientError as e:
        return {"error": f"An error occurred during file download from {url}: {e}"}

if __name__ == "__main__":
    transport = os.getenv("TRANSPORT", "").upper()
    if transport == "HTTP":
        port = os.getenv("PORT", "8000")
        try:
            port_int = int(port)
            mcp.run(transport="http", host="0.0.0.0", port=port_int)
        except ValueError:
            print(f"Invalid PORT value: {port}. Using default stdio transport.")
            mcp.run()
    else:
        mcp.run()
