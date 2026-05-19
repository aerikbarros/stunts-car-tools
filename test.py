from scan.scan import scan_directory

from parser.res_parser import (
    read_res_file,
    parse_res_map,
    extract_name,
    extract_id,
    extract_description,
    get_simd_block
)

from parser.simd_parser import (
    parse_simd,
    hex_dump
)

import sys


# =========================
# UI
# =========================

def show_car_list(cars):
    """
    Display all detected cars.
    """

    print("\n=== CARS FOUND ===\n")

    keys = list(cars.keys())

    for i, k in enumerate(keys):
        car = cars[k]

        status = "OK" if car.valid_format else "INVALID"

        print(f"[{i}] {k} | {car.type} | {status}")

    return keys


# =========================
# RES + SIMD INSPECTOR
# =========================

def inspect_car(car):
    """
    Inspect RES and SIMD data.
    """

    print("\n=== CAR INSPECTOR ===")

    try:

        # =========================
        # READ RES FILE
        # =========================

        data = read_res_file(car.res)

        res_map = parse_res_map(data)

        car_id = extract_id(data, res_map)
        car_name = extract_name(data, res_map)
        edes = extract_description(data, res_map)

        print(f"\nFile: {car.res}")

        print(f"ID (gsna): {car_id}")
        print(f"Name (gnam): {car_name}")

        # =========================
        # EDES
        # =========================

        print("\n--- EDES ---")
        print(edes)

        # =========================
        # BLOCK MAP
        # =========================

        print("\n--- Resource Blocks ---")

        for k, v in res_map.items():
            print(f"  {k} -> offset {hex(v)}")

        # =========================
        # SIMD
        # =========================

        simd = get_simd_block(data, res_map)

        if not simd:
            print("\nSIMD block not found.")
            return

        parsed = parse_simd(simd)

        print("\n=== SIMD PARSER ===")

        print(f"Block size: {parsed['size']} bytes")

        # =========================
        # BASIC CAR DATA
        # =========================

        print(f"\nNumber of gears: {parsed['gears']}")

        print(f"Car weight: {parsed['car_mass']}")
        print(f"Brake power: {parsed['brake_power']}")

        print(f"Idle RPM: {parsed['idle_rpm']}")
        print(f"Downshift RPM: {parsed['downshift_rpm']}")
        print(f"Upshift RPM: {parsed['upshift_rpm']}")
        print(f"Max RPM: {parsed['max_rpm']}")

        print(f"\nAero drag: {parsed['aero_drag']}")
        print(f"Grip: {parsed['grip']}")
        print(f"Air grip: {parsed['air_grip']}")

        print(f"\nCar height: {parsed['car_height']}")

        # =========================
        # GEAR RATIOS
        # =========================

        print("\n--- Gear Ratios ---")

        for i, ratio in enumerate(parsed["gear_ratios"]):
            print(f"Gear {i + 1}: {ratio}")

        # =========================
        # TORQUE CURVE
        # =========================

        print("\n--- Torque Curve ---")

        torque = parsed["torque_curve"]

        for i, value in enumerate(torque):
            print(f"{i:03}: {value}")

        # =========================
        # OPTIONAL HEX DUMP
        # =========================

        dump = input(
            "\nShow SIMD hex dump? (y/n): "
        ).strip().lower()

        if dump == 'y':

            print("\n=== SIMD HEX DUMP ===")

            print(hex_dump(simd))

    except Exception as e:

        print("\nError while reading RES/SIMD:")
        print(e)


# =========================
# MAIN
# =========================

def main():

    print("=== STUNTS CAR TOOL ===\n")

    base_dir = input(
        "Stunts folder: "
    ).strip()

    if not base_dir:

        print("Invalid path.")
        sys.exit(1)

    # =========================
    # SCAN DIRECTORY
    # =========================

    cars = scan_directory(base_dir)

    if not cars:

        print("\nNo cars were found.")
        sys.exit(0)

    keys = show_car_list(cars)

    # =========================
    # MAIN LOOP
    # =========================

    while True:

        try:

            choice = input(
                "\nChoose the car number (or 'q' to quit): "
            ).strip()

            if choice.lower() == 'q':

                print("Quitting...")
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

            print("\nQuitting...")
            break


# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    main()
