"""Start the demo:   python run.py

Then open http://127.0.0.1:5000 in your browser. Press CTRL+C to stop.
Set DEMO_DEBUG=1 to see detailed errors while developing (never during a presentation).
"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n  Sports Fund–SHA Beneficiary Management Demo (fictional data)")
    print("  Open http://127.0.0.1:5000 in your browser. Press CTRL+C to stop.\n")
    app.run(host="127.0.0.1", port=5000, debug=os.environ.get("DEMO_DEBUG") == "1")
