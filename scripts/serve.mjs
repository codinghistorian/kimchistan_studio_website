import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { build } from './build.mjs';

await build();
const root = resolve('dist');
const port = Number(process.env.PORT || 8000);
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png', '.woff2': 'font/woff2', '.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml' };

createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    let file = resolve(root, `.${pathname}`);
    if (file !== root && !file.startsWith(root + sep)) throw new Error('Invalid path');
    const info = await stat(file).catch(() => null);
    if (info?.isDirectory()) file = resolve(file, 'index.html');
    const body = await readFile(file).catch(() => null);
    if (!body) {
      response.writeHead(404, { 'Content-Type': types['.html'] });
      response.end(await readFile(resolve(root, '404.html')));
      return;
    }
    response.writeHead(200, { 'Content-Type': types[extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    response.end(body);
  } catch {
    response.writeHead(400, { 'Content-Type': 'text/plain' });
    response.end('Bad request');
  }
}).listen(port, '127.0.0.1', () => console.log(`KIMCHISTAN STUDIO: http://localhost:${port}\nRun npm run build after changing site content, or restart this preview.`));
