#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import asyncio
from aiohttp import web, ClientSession

bad_headers = ("accept-encoding", "content-encoding", "transfer-encoding", "content-length", "proxy-connection", "connection", "host")

async def fuckheaders(headers):
    h = {}
    for name, value in headers.items():
        if name.lower() not in bad_headers:
            h[name] = value
    h['Connection'] = "close"
    return h

async def factory(app, handler):
    async def fuck(request):
        print("==> %s" % request.host)
        method = request.method
        url = str(request.url)
        #url = str(request.url).replace("https://", "http://")
        headers = await fuckheaders(request.headers)
        data = await request.read()
        return await getresp(app.loop, method, url, headers, data)
    return fuck

async def getresp(loop, method, url, headers={}, data={}):
    async with ClientSession(loop=loop) as session:
        async with session.request(method, url, headers=headers, data=data) as resp:
            print("<== %s" % resp.host)
            body = await resp.read()
            headers = await fuckheaders(resp.headers)
            response = web.Response(body=body, status=resp.status, reason=resp.reason, headers=headers)
    return response

async def init(loop, port):
    app = web.Application(loop=loop, middlewares=[factory])
    return await loop.create_server(app.make_handler(), "", port)

def main():
    if len(sys.argv) < 2:
        print("Usage: %s <listen port>" % sys.argv[0])
        sys.exit(1)
    port = int(sys.argv[1])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop, port))
    loop.run_forever()

if __name__ == "__main__":
    main()

