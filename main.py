import threading
import socket
import webview
from app.server import app


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def run_flask(port: int) -> None:
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)


if __name__ == '__main__':
    port = get_free_port()
    print(f"[INFO] Запуск локального сервера на порту {port}...")

    flask_thread = threading.Thread(target=run_flask, args=(port,), daemon=True)
    flask_thread.start()

    window = webview.create_window(
        title="Password Forge",
        url=f"http://127.0.0.1:{port}",
        width=900,
        height=700,
        resizable=True,
        text_select=True
    )

    webview.start()