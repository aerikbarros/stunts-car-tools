from scan.scan import scan_directory
from parser.res_parser import (
    read_res_file,
    parse_res_map,
    extract_name,
    extract_id,
    extract_description,
    get_simd_block
)

import sys


def show_car_list(cars):
    print("\n=== CARS FOUND ===\n")

    keys = list(cars.keys())

    for i, k in enumerate(keys):
        car = cars[k]
        status = "OK" if car.valid_format else "INVALID"

        print(f"[{i}] {k} | {car.type} | {status}")

    return keys


def inspect_car(car):
    print("\n=== INSPECT RES ===")

    try:
        data = read_res_file(car.res)
        res_map = parse_res_map(data)

        print(f"\nFile: {car.res}")
        print(f"ID (gsna): {extract_id(data, res_map)}")
        print(f"Name (gnam): {extract_name(data, res_map)}")

        # EDES
        edes = extract_description(data, res_map)
        print("\n--- EDES ---")
        print(edes)

        # SIMD
        simd = get_simd_block(data, res_map)

        if simd:
            gears = simd[0]
            print("\n--- SIMD ---")
            print(f"Number of gears: {gears}")
        else:
            print("\n--- SIMD ---")
            print("Not Found")

        print("\n--- Blocks ---")
        for k, v in res_map.items():
            print(f"{k} → {hex(v)}")

    except Exception as e:
        print(f"RES Error: {e}")


def main():
    print("=== STUNTS CAR TOOL (TEST) ===\n")

    base_dir = input("Stunts folder: ").strip()

    if not base_dir:
        print("Invalid path.")
        sys.exit(1)

    cars = scan_directory(base_dir)

    if not cars:
        print("\nNo cars were found.")
        sys.exit(0)

    keys = show_car_list(cars)

    while True:
        try:
            choice = input("\nChoose the car number. (or 'q' to quit): ").strip()

            if choice.lower() == 'q':
                print("Quiting...")
                break

            idx = int(choice)

            if idx < 0 or idx >= len(keys):
                print("Invalid number.")
                continue

            selected_key = keys[idx]
            car = cars[selected_key]

            inspect_car(car)

        except ValueError:
            print("Enter a valid number.")
        except KeyboardInterrupt:
            print("\nQuiting...")
            break


if __name__ == "__main__":
    main()
