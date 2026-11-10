import asyncio
import os
from pathlib import Path
import socket
import subprocess
import sysconfig
import tempfile
import time
from urllib.request import urlopen

from aiohttp import web
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
import magic
import pytest

from file_convert_mcp import server


@pytest.fixture
def work_dir():
    # Large boundary-test files live in TEMP and are removed after each test.
    with tempfile.TemporaryDirectory(prefix="file-convert-mcp-test-", ignore_cleanup_errors=True) as folder:
        yield Path(folder)


async def conversion_case(monkeypatch, source, *, outputs=1, failed_output=None):
    uploads = []

    async def upload(request):
        part = await (await request.multipart()).next()
        size = 0
        while chunk := await part.read_chunk():
            size += len(chunk)
        uploads.append(size)
        return web.json_response({"Filename": "uploaded.bin"})

    async def convert(request):
        assert (await request.json())["ext_out"] == "txt"
        return web.json_response({"file": {
            "ext_out": "txt", "urls": [f"/result/{n}" for n in range(outputs)]
        }})

    async def result(request):
        n = int(request.match_info["n"])
        if n == failed_output:
            return web.Response(status=500, text="Test download failure")
        return web.Response(body=f"Result {n}".encode())

    app = web.Application()
    app.router.add_post('/api/v1/upload', upload)
    app.router.add_post('/api/v1/convert', convert)
    app.router.add_get('/result/{n}', result)
    runner = web.AppRunner(app)
    await runner.setup()
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    await web.SockSite(runner, sock).start()
    monkeypatch.setattr(server, 'base_url', f'http://127.0.0.1:{port}')
    try:
        response = await server.convert_file.fn(str(source), 'TXT')
        return response, uploads
    finally:
        await runner.cleanup()


@pytest.mark.parametrize('offset', [-1, 0, 1])
def test_upload_size_boundary(monkeypatch, work_dir, offset):
    source = work_dir / 'boundary.bin'
    size = server.MAX_FILE_SIZE + offset
    with source.open('wb') as f:
        f.truncate(size)
    response, uploads = asyncio.run(conversion_case(monkeypatch, source))
    if offset > 0:
        assert '40 MiB' in response['error']
        assert uploads == []
    else:
        assert uploads == [size]
        assert Path(response['result']['converted_file_path']).read_bytes() == b'Result 0'


def test_multiple_results_and_repeated_conversion(monkeypatch, work_dir):
    source = work_dir / 'input.bin'
    source.write_bytes(b'input')
    original = work_dir / 'input.bin.converted.txt'
    original.write_bytes(b'Keep me')
    seen = set()
    for _ in range(2):
        response, uploads = asyncio.run(conversion_case(monkeypatch, source, outputs=3))
        paths = response['result']['converted_file_paths']
        assert response['result']['converted_file_path'] == paths[0]
        assert len(paths) == 3
        for n, path in enumerate(paths):
            assert path not in seen
            seen.add(path)
            assert Path(path).read_bytes() == f'Result {n}'.encode()
        assert uploads == [5]
    assert original.read_bytes() == b'Keep me'
    assert source.read_bytes() == b'input'


def test_failed_download_reports_completed_files(monkeypatch, work_dir):
    source = work_dir / 'input.bin'
    source.write_bytes(b'input')
    response, _ = asyncio.run(conversion_case(monkeypatch, source, outputs=3, failed_output=1))
    assert '500' in response['error']
    paths = response['result']['converted_file_paths']
    assert len(paths) == 1
    assert Path(paths[0]).read_bytes() == b'Result 0'


def installed_command():
    scheme = 'nt_user' if os.name == 'nt' else 'posix_user'
    suffix = '.exe' if os.name == 'nt' else ''
    command = Path(sysconfig.get_path('scripts', scheme)) / f'file-convert-mcp{suffix}'
    assert command.is_file(), 'Install the package before running the transport tests.'
    return str(command)


async def check_mcp(transport):
    async with Client(transport, timeout=10) as client:
        tools = await client.list_tools()
        assert {tool.name for tool in tools} == {'detect_file_type', 'convert_file'}
        # An actual tool call, deliberately rejected before any external API request.
        response = await client.call_tool('convert_file', {'file_path': '', 'ext_out': 'txt'})
        assert 'file_path parameter is required' in str(response)
        response2 = await client.call_tool('detect_file_type', {'file_path': ''})
        assert 'file_path parameter is required' in str(response2)


@pytest.mark.parametrize('port', [None, 'invalid'])
def test_installed_stdio_start(work_dir, port):
    env = dict(os.environ, PYTHONIOENCODING='utf-8', TRANSPORT='stdio')
    if port:
        env.update(TRANSPORT='http', PORT=port)
    transport = StdioTransport(command=installed_command(), args=[], env=env, cwd=str(work_dir))
    asyncio.run(check_mcp(transport))


def test_installed_http_start(work_dir):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = dict(os.environ, PYTHONIOENCODING='utf-8', TRANSPORT='http', PORT=str(port))
    log_path = work_dir / 'http.log'
    with log_path.open('w', encoding='utf-8') as log:
        process = subprocess.Popen(
            [installed_command()], env=env, cwd=work_dir,
            stdout=log, stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
        )
        try:
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                assert process.poll() is None, log_path.read_text(encoding='utf-8')
                try:
                    with urlopen(f'http://127.0.0.1:{port}/health', timeout=1) as response:
                        assert response.status == 200
                    break
                except OSError:
                    time.sleep(0.1)
            else:
                pytest.fail(log_path.read_text(encoding='utf-8'))
            with urlopen(f'http://127.0.0.1:{port}/tools', timeout=2) as response:
                assert b'convert_file' in response.read()
            asyncio.run(check_mcp(f'http://127.0.0.1:{port}/mcp'))
        finally:
            process.terminate()
            process.wait(timeout=10)


def test_native_file_detection():
    assert magic.from_buffer(b'%PDF-1.4\n', mime=True) == 'application/pdf'
