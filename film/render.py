import asyncio, base64, subprocess, sys
from pathlib import Path
from playwright.async_api import async_playwright
FPS = 30
frames = sys.argv[1] if len(sys.argv) > 1 else 'all'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1280, 'height': 720})
        await pg.goto(Path(__file__).with_name('khong.html').resolve().as_uri())
        await pg.evaluate('window.ready')
        dur = await pg.evaluate('window.DUR')
        if frames != 'all':
            for t in [float(x) for x in frames.split(',')]:
                data = await pg.evaluate(f"(render({t}), document.getElementById('c').toDataURL('image/png'))")
                open(f'./f_{t}.png', 'wb').write(base64.b64decode(data.split(',')[1]))
            await b.close(); return
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart',
                               './khong.mp4'], stdin=subprocess.PIPE)
        n = int(dur * FPS)
        for i in range(n):
            data = await pg.evaluate(f"(render({i / FPS}), document.getElementById('c').toDataURL('image/jpeg', 0.95))")
            ff.stdin.write(base64.b64decode(data.split(',')[1]))
            if i % 300 == 0: print('frame', i, '/', n, flush=True)
        ff.stdin.close(); ff.wait()
        await b.close()
asyncio.run(main())
