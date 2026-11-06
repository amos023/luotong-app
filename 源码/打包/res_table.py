"""生成最小可用的 resources.arsc：只有一个 mipmap 图标条目。

没有 aapt2 时，系统要解析 @mipmap/ic_launcher 这类引用就必须有资源表，
因此这里按 ResTable 的二进制结构手工拼一份。
"""
import struct

RES_TABLE = 0x0002
RES_STRING_POOL = 0x0001
RES_TABLE_PACKAGE = 0x0200
RES_TABLE_TYPE_SPEC = 0x0202
RES_TABLE_TYPE = 0x0201

TYPE_STRING = 0x03


def string_pool(strings, utf8=False):
    """构造 ResStringPool（默认 UTF-16，简单可靠）。"""
    count = len(strings)
    data = bytearray()
    offsets = []
    for s in strings:
        offsets.append(len(data))
        if utf8:
            raw = s.encode("utf-8")
            data += bytes([len(raw)]) + bytes([len(raw)]) + raw + b"\x00"
        else:
            enc = s.encode("utf-16-le")
            data += struct.pack("<H", len(enc) // 2) + enc + b"\x00\x00"
    while len(data) % 4:
        data += b"\x00"
    header_size = 28
    strings_start = header_size + 4 * count
    size = strings_start + len(data)
    flags = 0x100 if utf8 else 0
    out = bytearray()
    out += struct.pack("<HHI", RES_STRING_POOL, header_size, size)
    out += struct.pack("<IIIII", count, 0, flags, strings_start, 0)
    if count:
        out += struct.pack("<%dI" % count, *offsets)
    out += data
    return bytes(out)


def build(package_name=b"io.github.mcool.luotong",
          type_name="mipmap",
          entry_name="ic_launcher",
          value_path="res/mipmap-xhdpi/ic_launcher.png",
          package_id=0x7F):
    global_pool = string_pool([value_path])

    type_pool = string_pool([type_name])
    key_pool = string_pool([entry_name])

    # ---- TypeSpec ----
    entry_count = 1
    ts_size = 16 + 4 * entry_count
    type_spec = bytearray()
    type_spec += struct.pack("<HHI", RES_TABLE_TYPE_SPEC, 16, ts_size)
    type_spec += struct.pack("<BBHI", 1, 0, 0, entry_count)
    type_spec += struct.pack("<I", 0)  # 无配置变化

    # ---- Type（默认配置）----
    config = struct.pack("<I", 56) + b"\x00" * 52
    header_size = 20 + len(config)
    entries_start = header_size + 4 * entry_count  # 偏移表在 header 之后
    entry = struct.pack("<HHI", 8, 0, 0)           # ResTable_entry：size, flags, key
    entry += struct.pack("<HBBI", 8, 0, TYPE_STRING, 0)  # Res_value：指向全局池第 0 项
    type_size = entries_start + len(entry)
    typ = bytearray()
    typ += struct.pack("<HHI", RES_TABLE_TYPE, header_size, type_size)
    typ += struct.pack("<BBHII", 1, 0, 0, entry_count, entries_start)
    typ += config
    typ += struct.pack("<I", 0)  # 第 0 项在 entries_start 处
    typ += entry

    # ---- Package ----
    # ResTable_package 的 name 是 char16[128]，即 256 字节
    name_bytes = package_name.decode("utf-8").encode("utf-16-le")[:254].ljust(256, b"\x00")
    type_strings_off = 288
    key_strings_off = type_strings_off + len(type_pool)
    body = type_pool + key_pool + bytes(type_spec) + bytes(typ)
    pkg_size = 288 + len(body)
    pkg = bytearray()
    pkg += struct.pack("<HHI", RES_TABLE_PACKAGE, 288, pkg_size)
    pkg += struct.pack("<I", package_id)
    pkg += name_bytes
    pkg += struct.pack("<IIIII", type_strings_off, 1, key_strings_off, 1, 0)
    pkg += body

    total = 12 + len(global_pool) + len(pkg)
    out = bytearray()
    out += struct.pack("<HHII", RES_TABLE, 12, total, 1)
    out += global_pool
    out += pkg
    return bytes(out)


if __name__ == "__main__":
    data = build()
    open("/workspace/项目/落筒录入APK/out/resources.arsc", "wb").write(data)
    print("resources.arsc:", len(data), "bytes")
