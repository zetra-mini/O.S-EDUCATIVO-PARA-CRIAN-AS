import urllib.request
import time
import json

endpoints = [
    ('/', 'HUD Jarvis (Modo Kiosk Criança)'),
    ('/admin', 'Painel Administrativo dos Pais'),
    ('/engenharia', 'Quarto de Engenharia (Blockly)'),
    ('/volume', 'API de Volume ALSA / Sistema'),
    ('/api/state', 'API de Estado Geral'),
    ('/api/missoes', 'API de Missões do Herói (Kiosk)'),
    ('/api/admin/nuvem/status', 'API de Status da Nuvem Cloudflare'),
    ('/api/admin/hardware/wifi/status', 'API de Status Wi-Fi Conectado'),
    ('/api/admin/hardware/wifi/scan', 'API de Varredura Wi-Fi Completa'),
    ('/api/admin/missoes', 'API de Missões dos Pais'),
    ('/api/admin/arte', 'API da Galeria de Arte Neon'),
    ('/api/admin/linha_tempo', 'API da Linha do Tempo Diária'),
    ('/api/cognicao/descobre_som/novo', 'API Jogo Descobre o Som'),
    ('/static/assets_poupy/musica/BoxCat%20Games%20-%20Young%20Love.mp3', 'Áudio BoxCat Games (Timer/Dente)')
]

print("=== INICIANDO BATERIA DE TESTES NO LOCALHOST:8000 ===\n")
total_ok = 0

for path, desc in endpoints:
    url = f"http://localhost:8000{path}"
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'JarvisTester/1.0'})
        with urllib.request.urlopen(req, timeout=8) as res:
            elapsed = (time.time() - t0) * 1000
            status = res.status
            ctype = res.headers.get('Content-Type', '')
            length = len(res.read())
            print(f"[OK] {status} | {elapsed:5.1f}ms | {desc} -> {path} ({length} bytes, {ctype})")
            total_ok += 1
    except Exception as e:
        print(f"[FALHA] {desc} -> {path}: {e}")

print(f"\nResultado Final: {total_ok}/{len(endpoints)} endpoints responderam com sucesso!")
