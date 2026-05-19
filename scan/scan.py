from pathlib import Path
from models.car import Car
import argparse

# =========================
# CORE (SCAN)
# =========================

VALID_EXTENSIONS = {'.3sh', '.p3s', '.vsh', '.pvs', '.res'}


def scan_directory(base_dir):
    base_dir = Path(base_dir)

    if not base_dir.exists():
        return {}

    cars = {}

    for file in base_dir.iterdir():
        if not file.is_file():
            continue

        ext = file.suffix.lower()
        if ext not in VALID_EXTENSIONS:
            continue

        prefix, comp_type = identify_component(file.name.lower(), ext)

        if not prefix:
            continue

        if prefix not in cars:
            cars[prefix] = Car()

        assign_component(cars[prefix], comp_type, file)

    result = {}

    for k, car in cars.items():
        if car.is_valid():
            classify_car(car)
            result[k] = car

    return result


def identify_component(filename, ext):
    if filename.startswith('stda') and ext in ('.vsh', '.pvs'):
        return filename[4:8].upper(), 'pvs_static'

    if filename.startswith('stdb') and ext in ('.vsh', '.pvs'):
        return filename[4:8].upper(), 'pvs_moving'

    if filename.startswith('st') and ext in ('.3sh', '.p3s'):
        return filename[2:6].upper(), 'p3s'

    if filename.startswith('car') and ext == '.res':
        return filename[3:7].upper(), 'res'

    return None, None


def assign_component(car, comp_type, file_path):
    ext = file_path.suffix.lower()

    if getattr(car, comp_type) is None:
        setattr(car, comp_type, str(file_path))

    if comp_type == 'p3s':
        car.ext_3d = ext
        car.is_compressed_3d = (ext == '.p3s')

    if comp_type in ('pvs_static', 'pvs_moving'):
        car.ext_pvs = ext
        car.is_compressed_pvs = (ext == '.pvs')


def classify_car(car):

    if car.is_compressed_3d is None or car.is_compressed_pvs is None:
        car.type = "!!invalid!!"
        car.valid_format = False
        return

    # ORIGINAL
    if car.is_compressed_3d and car.is_compressed_pvs:
        car.type = "original"
        car.valid_format = True
        return

    # CUSTOM
    if car.is_compressed_3d is False and car.is_compressed_pvs is False:
        car.type = "custom  "
        car.valid_format = True
        return

    # INVALID
    car.type = "invalid"
    car.valid_format = False


def serialize_cars(cars):
    output = {}

    for k, v in cars.items():
        output[k] = {
            "p3s": v.p3s,
            "pvs_static": v.pvs_static,
            "pvs_moving": v.pvs_moving,
            "res": v.res,
            "ext_3d": v.ext_3d,
            "ext_pvs": v.ext_pvs,
            "type": v.type,
            "valid_format": getattr(v, "valid_format", None),
            "is_compressed_3d": v.is_compressed_3d,
            "is_compressed_pvs": v.is_compressed_pvs
        }

    return output


# =========================
# CLI
# =========================

def run_cli():
    parser = argparse.ArgumentParser(description="Car Scanner")
    parser.add_argument("command", choices=["scan"])
    parser.add_argument("--dir", default="stunts")

    args = parser.parse_args()

    if args.command == "scan":
        cars = scan_directory(args.dir)

        print(f"\n{len(cars)} cars found\n")

        for k, car in cars.items():
            status = "OK" if car.valid_format else "INVALID"

            print(
                f"{k} | {car.type.upper():8} | {status} | "
                f"3D:{car.ext_3d} | PVS:{car.ext_pvs}"
            )


# =========================
# API WEB
# =========================

def create_app():
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/scan")
    def scan(dir: str = "stunts"):
        cars = scan_directory(dir)

        return {
            "total": len(cars),
            "cars": serialize_cars(cars)
        }

    return app


# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    run_cli()
