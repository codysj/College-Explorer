"""Write the API's OpenAPI schema to stdout, for generating the frontend's types.

Builds the app in-process, so no server or database is needed:
    python apps/api/scripts/export_openapi.py > apps/web/types/openapi.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import create_app  # noqa: E402

sys.stdout.reconfigure(newline="\n")  # identical bytes on Windows and Linux, for the CI diff
print(json.dumps(create_app().openapi(), indent=2, sort_keys=True))
