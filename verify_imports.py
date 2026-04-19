import os
import sys
import traceback

project_root = os.path.abspath(os.path.dirname(__file__))
os.chdir(project_root)
sys.path.insert(0, project_root)
modules = [
    "app",
    "app.auth",
    "app.extensions",
    "app.forms",
    "app.models",
    "app.utils",
    "app.weather_service",
    "app.routes.main_routes",
    "app.routes.farmer_routes",
    "app.routes.admin_routes",
    "app.routes.auth_routes",
    "app.routes.crop_predict",
    "app.routes.chatbot_routes",
    "app.ml_model.crop_prediction",
    "app.ml_model.train_model",
]

missing = []
loaded = []
print("IMPORT CHECK")
for mod in modules:
    try:
        __import__(mod)
        print(f"OK: {mod}")
        loaded.append(mod)
    except Exception as e:
        print(f"FAIL: {mod} -> {type(e).__name__}: {e}")
        traceback.print_exc()
        missing.append((mod, e))

print("\nSUMMARY:")
print(f"loaded={len(loaded)} missing={len(missing)}")
if missing:
    print("Missing or failing imports:")
    for mod, err in missing:
        print(f"- {mod}: {type(err).__name__}: {err}")
