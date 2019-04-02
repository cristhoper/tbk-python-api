def hex_string(s, crc=False):
    if crc:
        crc_val = get_hex_crc(s[1:])
        c = s + crc_val
        return bytes(c)
    return bytes(s)


def get_hex_crc(s):
    crc_bytes = bytearray(s, 'utf-8')
    checksum = crc_bytes[0]
    for e in crc_bytes[1:len(crc_bytes)]:
        checksum ^= e
    return chr(checksum)

