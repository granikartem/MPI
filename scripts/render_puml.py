import argparse
import subprocess
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Render PlantUML .puml diagrams to images using plantuml.jar"
    )
    ap.add_argument("--jar", required=True, help="Path to plantuml.jar")
    ap.add_argument(
        "--src",
        default="diagrams/usecases",
        help="Folder with .puml files (default: diagrams/usecases)",
    )
    ap.add_argument(
        "--out",
        default="diagrams/out",
        help="Output folder for rendered images (default: diagrams/out)",
    )
    ap.add_argument(
        "--fmt",
        default="png",
        choices=["png", "svg"],
        help="Output image format (png or svg)",
    )
    args = ap.parse_args()

    jar = Path(args.jar)
    if not jar.exists():
        raise SystemExit(f"plantuml.jar not found: {jar}")

    src = Path(args.src)
    if not src.exists():
        raise SystemExit(f"Source folder not found: {src}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    puml_files = sorted(src.rglob("*.puml"))
    if not puml_files:
        raise SystemExit(f"No .puml files found in: {src}")

    cmd = [
        "java",
        "-DPLANTUML_LIMIT_SIZE=16384",
        "-jar",
        str(jar),
        f"-t{args.fmt}",
        "-o",
        str(out.resolve()),
        *[str(p) for p in puml_files],
    ]
    subprocess.check_call(cmd)
    print(f"Rendered {len(puml_files)} diagram(s) to {out} as {args.fmt}")


if __name__ == "__main__":
    main()
