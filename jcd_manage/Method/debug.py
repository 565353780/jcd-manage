import struct


#debug函数
def parse_4_bytes(bytes_data):
    if len(bytes_data) < 4:
        print(f"unkown data {len(bytes_data)} bytes, unkown_data: {bytes_data}")
        return

    float_value = struct.unpack('<f', bytes_data)[0]
    int_value = struct.unpack('<i', bytes_data)[0]
    short1, short2 = struct.unpack('<hh', bytes_data)
    print(f"float: {float_value}, int: {int_value}, shorts: ({short1}, {short2}), original: {bytes_data.hex()} {bytes_data}")
    return
