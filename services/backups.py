import os, zipfile, io, json
from datetime import datetime
import pytz
from core.config import settings

# ---- IST TIME ----
IST = pytz.timezone("Asia/Kolkata")
def now_ist():
    return datetime.now(IST)

def ensure_local_dir():
    os.makedirs(settings.local_backup_dir, exist_ok=True)

def backup_proposal(reference_no: str, artifacts: dict[str, bytes] | None = None, meta: dict | None = None) -> dict:
    """Create a ZIP backup with files and metadata.
    artifacts: mapping of filename -> bytes content (e.g., generated docx/pdf)
    meta: arbitrary metadata dict
    Returns paths for local zip.
    """
    ensure_local_dir()

    # ✅ IST timestamp
    ts = now_ist().strftime('%Y%m%d_%H%M%S')

    zip_name = f"{reference_no}_{ts}.zip"
    local_path = os.path.join(settings.local_backup_dir, zip_name)

    # Build zip in memory
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, 'w', zipfile.ZIP_DEFLATED) as zf:
        if meta:
            zf.writestr('meta.json', json.dumps(meta, indent=2, default=str))
        if artifacts:
            for fname, blob in artifacts.items():
                zf.writestr(fname, blob)

    with open(local_path, 'wb') as f:
        f.write(mem.getvalue())

    return {"local_path": local_path}
