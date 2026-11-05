import traceback
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    from simulador_web import app
    app.run(host="0.0.0.0", port=5090, debug=False, threaded=True)
except Exception:
    with open("crash.log", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
