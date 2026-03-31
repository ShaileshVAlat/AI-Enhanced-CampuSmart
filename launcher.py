# launch.py
import os
import sys
import subprocess
import time


def start_app(script: str, port: str):
    env = os.environ.copy()
    env["STREAMLIT_SERVER_PORT"] = port
    env["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", script
    ], env=env)


if __name__ == "__main__":
    ats_proc = start_app("app.py", "1111")
    chat_proc = start_app("chatbot.py", "2222")

    # Wait a moment for startup
    time.sleep(3)
    print("\n✅ Apps launched:\n  ATS ➜ http://localhost:1111\n  Chatbot ➜ http://localhost:2222\n")
    print("Press Ctrl+C to stop both apps.")

    try:
        ats_proc.wait()
        chat_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down both apps…")
        ats_proc.terminate()
        chat_proc.terminate()
        sys.exit(0)