"""Replace dx's default launcher icon in a generated Android project with the quest icon.

dx 0.7 always writes its own ic_launcher resources, so CI runs this on the generated
`app/src/main/res` folder and then reassembles the APK with Gradle.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "assets/icon"
DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}


def apply(res):
    for name in ("drawable/ic_launcher_background.xml", "drawable-v24/ic_launcher_foreground.xml"):
        (res / name).unlink(missing_ok=True)
    (res / "values").mkdir(parents=True, exist_ok=True)
    (res / "values/ic_launcher_colors.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#173D36</color>\n</resources>\n',
        encoding="utf-8",
    )
    for density, size in DENSITIES.items():
        folder = res / f"mipmap-{density}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "ic_launcher.webp").unlink(missing_ok=True)
        shutil.copy(ICONS / f"icon-{size}.png", folder / "ic_launcher.png")
    foreground = res / "mipmap-xxxhdpi/ic_launcher_foreground.png"
    shutil.copy(ICONS / "icon-foreground.png", foreground)
    (res / "mipmap-anydpi-v26").mkdir(parents=True, exist_ok=True)
    (res / "mipmap-anydpi-v26/ic_launcher.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/ic_launcher_background" />\n'
        '    <foreground android:drawable="@mipmap/ic_launcher_foreground" />\n'
        "</adaptive-icon>\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    res = Path(sys.argv[1])
    if not (res / "mipmap-anydpi-v26").is_dir():
        sys.exit(f"{res} is not a generated Android res folder")
    apply(res)
    print("quest icon applied to", res)
