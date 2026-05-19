import struct


# =========================
# HELPERS
# =========================

def read_uint8(data, offset):
    return struct.unpack_from('<B', data, offset)[0]


def read_int16(data, offset):
    return struct.unpack_from('<H', data, offset)[0]


# =========================
# PARSER
# =========================

def parse_simd(simd):
    if not simd:
        return None

    result = {}

    result["size"] = len(simd)

    # =========================
    # ENGINE / TRANSMISSION
    # =========================

    result["gears"] = read_uint8(simd, 0x00)

    result["car_mass"] = read_int16(simd, 0x02)

    result["brake_power"] = read_int16(simd, 0x04)

    result["idle_rpm"] = read_int16(simd, 0x06)

    result["downshift_rpm"] = read_int16(simd, 0x08)

    result["upshift_rpm"] = read_int16(simd, 0x0A)

    result["max_rpm"] = read_int16(simd, 0x0C)

    result["aero_drag"] = read_int16(simd, 0x38)

    result["idle_torque"] = read_uint8(simd, 0x3A)

    result["grip"] = read_int16(simd, 0xA4)

    result["air_grip"] = read_int16(simd, 0xB4)

    result["car_height"] = read_int16(simd, 0xD0)

    # gear ratios
    gear_ratios = []

    for i in range(6):
        gear_ratios.append(read_uint8(simd, 0x10 + i))

    result["gear_ratios"] = gear_ratios

    # torque curve
    torque_curve = []

    for i in range(103):
        torque_curve.append(read_uint8(simd, 0x3B + i))

    result["torque_curve"] = torque_curve

    return result


# =========================
# DEBUG
# =========================

def hex_dump(data, width=16):
    lines = []

    for i in range(0, len(data), width):
        chunk = data[i:i+width]

        hex_part = ' '.join(f'{b:02X}' for b in chunk)

        ascii_part = ''.join(
            chr(b) if 32 <= b <= 126 else '.'
            for b in chunk
        )

        lines.append(f'{i:04X}  {hex_part:<48}  {ascii_part}')

    return '\n'.join(lines)