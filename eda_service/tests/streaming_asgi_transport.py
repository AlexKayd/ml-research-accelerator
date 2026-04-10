from __future__ import annotations
import asyncio
import typing
from httpx import Request, Response
from httpx._transports.base import AsyncBaseTransport
from httpx._types import AsyncByteStream

_ASGIApp = typing.Callable[
    [typing.Dict[str, typing.Any], typing.Any, typing.Any],
    typing.Coroutine[typing.Any, typing.Any, None],
]


class _QueueAsyncByteStream(AsyncByteStream):
    def __init__(
        self,
        queue: asyncio.Queue[bytes | None],
        stream_closed: asyncio.Event,
        app_task: asyncio.Task[None],
        end_stream: typing.Callable[[], typing.Awaitable[None]],
    ) -> None:
        self._queue = queue
        self._stream_closed = stream_closed
        self._app_task = app_task
        self._end_stream = end_stream
        self._closed = False

    async def __aiter__(self) -> typing.AsyncIterator[bytes]:
        while True:
            item = await self._queue.get()
            if item is None:
                break
            yield item

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        if not self._app_task.done():
            self._app_task.cancel()
            try:
                await self._app_task
            except asyncio.CancelledError:
                pass
            except BaseException:
                pass
        await self._end_stream()


class StreamingBodyASGITransport(AsyncBaseTransport):
    def __init__(
        self,
        app: _ASGIApp,
        *,
        raise_app_exceptions: bool = True,
        root_path: str = "",
        client: tuple[str, int] = ("127.0.0.1", 123),
    ) -> None:
        self.app = app
        self.raise_app_exceptions = raise_app_exceptions
        self.root_path = root_path
        self.client = client

    async def handle_async_request(self, request: Request) -> Response:
        assert isinstance(request.stream, AsyncByteStream)

        scope: dict[str, typing.Any] = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": request.method,
            "headers": [(k.lower(), v) for (k, v) in request.headers.raw],
            "scheme": request.url.scheme,
            "path": request.url.path,
            "raw_path": request.url.raw_path,
            "query_string": request.url.query,
            "server": (request.url.host, request.url.port),
            "client": self.client,
            "root_path": self.root_path,
        }

        request_body_chunks = request.stream.__aiter__()
        request_complete = False

        status_code: int | None = None
        response_headers: list[tuple[bytes, bytes]] | None = None
        headers_sent = asyncio.Event()
        stream_closed = asyncio.Event()
        body_queue: asyncio.Queue[bytes | None] = asyncio.Queue()
        ended = False

        async def end_stream_once() -> None:
            nonlocal ended
            if ended:
                return
            ended = True
            await body_queue.put(None)
            stream_closed.set()

        async def receive() -> dict[str, typing.Any]:
            nonlocal request_complete
            if request_complete:
                await stream_closed.wait()
                return {"type": "http.disconnect"}
            try:
                body = await request_body_chunks.__anext__()
            except StopAsyncIteration:
                request_complete = True
                return {"type": "http.request", "body": b"", "more_body": False}
            return {"type": "http.request", "body": body, "more_body": True}

        async def send(message: dict[str, typing.Any]) -> None:
            nonlocal status_code, response_headers
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = message.get("headers", [])
                headers_sent.set()
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                more_body = message.get("more_body", False)
                if body and request.method != "HEAD":
                    await body_queue.put(body)
                if not more_body:
                    await end_stream_once()

        async def run_app() -> None:
            try:
                await self.app(scope, receive, send)
            except asyncio.CancelledError:
                raise
            except Exception:
                if self.raise_app_exceptions:
                    raise
            finally:
                await end_stream_once()

        app_task = asyncio.create_task(run_app())

        try:
            await asyncio.wait_for(headers_sent.wait(), timeout=120.0)
        except Exception:
            if not app_task.done():
                app_task.cancel()
                try:
                    await app_task
                except asyncio.CancelledError:
                    pass
            raise

        if app_task.done() and (exc := app_task.exception()) is not None:
            raise exc

        assert status_code is not None and response_headers is not None

        stream = _QueueAsyncByteStream(body_queue, stream_closed, app_task, end_stream_once)
        return Response(status_code, headers=response_headers, stream=stream)