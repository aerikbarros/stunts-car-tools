from pathlib import Path
import struct
import argparse

HEADER_SIZE = 0x26  # 38 bytes


# =========================
# CORE (RES PARSE)
# =========================

def read_res_file(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "rb") as f:
        return f.read()


def parse_res_map(data):
    if len(data) < 10:
        return {}

    try:
        n = struct.unpack_from('<H', data, 4)[0]
    except:
        return {}

    if n <= 0 or n > 100:
        return {}

    res_map = {}
    base = 6

    for i in range(n):
        try:
            rid_offset = base + i * 4
            off_offset = base + n * 4 + i * 4

            if rid_offset + 4 > len(data):
                continue

            if off_offset + 4 > len(data):
                continue

            rid_bytes = data[rid_offset:rid_offset + 4]
            rid = rid_bytes.decode('ascii', errors='ignore').strip()

            off = struct.unpack_from('<I', data, off_offset)[0]

            real_offset = off + HEADER_SIZE

            if real_offset >= len(data):
                continue

            res_map[rid] = real_offset

        except:
            continue

    return res_map


# =========================
# EXTRACTION
# =========================

def extract_string(data, offset):
    end = offset

    while end < len(data) and data[end] != 0:
        end += 1

    try:
        return data[offset:end].decode('ascii', errors='replace')
    except:
        return None


def extract_id(data, res_map):
    if 'gsna' not in res_map:
        return None

    off = res_map['gsna']
    raw = data[off:off+4]

    try:
        return raw.decode('ascii', errors='replace')
    except:
        return None


def extract_name(data, res_map):
    if 'gnam' in res_map:
        name = extract_string(data, res_map['gnam'])

        if name and len(name) < 50:
            return name

    if 'edes' in res_map:
        return extract_description(data, res_map)

    return None


def extract_description(data, res_map):
    if 'edes' not in res_map:
        return None

    start = res_map['edes']

    try:
        file_size = struct.unpack_from('<I', data, 0)[0]
    except:
        file_size = len(data)

    if file_size > len(data):
        file_size = len(data)

    raw = data[start:file_size]

    try:
        return raw.decode('ascii', errors='replace').strip()
    except:
        return None


def parse_description_fields(text):
    if not text:
        return []

    parts = text.split(']')
    return [p.strip() for p in parts if p.strip()]


def get_simd_block(data, res_map):
    if 'simd' not in res_map:
        return None

    start = res_map['simd']

    offsets = sorted(res_map.values())
    current_index = offsets.index(start)

    if current_index + 1 < len(offsets):
        end = offsets[current_index + 1]
    else:
        end = len(data)

    return data[start:end]


# =========================
# INSPECTOR
# =========================

def inspect_res(path):
    data = read_res_file(path)
    res_map = parse_res_map(data)

    description = extract_description(data, res_map)

    return {
        "file": str(path),
        "file_size": len(data),
        "total_blocks": len(res_map),
        "blocks": res_map,
        "id": extract_id(data, res_map),
        "name": extract_name(data, res_map),
        "description": description,
        "description_fields": parse_description_fields(description)
    }


# =========================
# CLI
# =========================

def run_cli():
    parser = argparse.ArgumentParser(description="RES Parser")
    parser.add_argument("command", choices=["inspect"])
    parser.add_argument("--file", required=True)

    args = parser.parse_args()

    if args.command == "inspect":
        info = inspect_res(args.file)

        print("\n=== RES INSPECT ===")
        print(f"File: {info['file']}")
        print(f"Size: {info['file_size']} bytes")
        print(f"Blocks: {info['total_blocks']}")

        print(f"\nID (gsna): {info['id']}")
        print(f"Name: {info['name']}")

        print("\n--- EDES ---")
        print(info["description"])

        print("\n--- Fields ---")
        for f in info["description_fields"]:
            print(f"  - {f}")

        print("\n--- Blocks ---")
        for k, v in info["blocks"].items():
            print(f"{k} → {hex(v)}")


# =========================
# API WEB
# =========================

def create_app():
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/inspect_res")
    def inspect(file: str):
        return inspect_res(file)

    return app


# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    run_cli()
