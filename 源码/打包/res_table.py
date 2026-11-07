"""生成 resources.arsc：一个 mipmap 图标条目，按 5 档屏幕密度分别指向不同 png。

没有 aapt2 时，系统要解析 @mipmap/ic_launcher 必须有资源表。
这里按 ResTable 结构手拼，并为每个密度写一个 ResTable_type（config 里带 density），
这样 560dpi 设备会取 xxxhdpi 那档，而不是把低密度图放大导致模糊。
"""
import struct

RES_TABLE = 0x0002
RES_STRING_POOL = 0x0001
RES_TABLE_PACKAGE = 0x0200
RES_TABLE_TYPE_SPEC = 0x0202
RES_TABLE_TYPE = 0x0201

TYPE_STRING = 0x03

# 密度名 → (density dpi, 资源路径)
DENSITIES = [
    ("mdpi", 160),
    ("hdpi", 240),
    ("xhdpi", 320),
    ("xxhdpi", 480),
    ("xxxhdpi", 640),
]


def string_pool(strings):
    """ResStringPool，UTF-16。"""
    count = len(strings)
    data = bytearray()
    offsets = []
    for s in strings:
        offsets.append(len(data))
        enc = s.encode("utf-16-le")
        data += struct.pack("<H", len(enc) // 2) + enc + b"\x00\x00"
    while len(data) % 4:
        data += b"\x00"
    header_size = 28
    strings_start = header_size + 4 * count
    size = strings_start + len(data)
    out = bytearray()
    out += struct.pack("<HHI", RES_STRING_POOL, header_size, size)
    out += struct.pack("<IIIII", count, 0, 0, strings_start, 0)
    if count:
        out += struct.pack("<%dI" % count, *offsets)
    out += data
    return bytes(out)


def make_config(density):
    """ResTable_config，56 字节；density 位于偏移 14（screenType 的后两字节）。"""
    cfg = bytearray(56)
    struct.pack_into("<I", cfg, 0, 56)      # size
    struct.pack_into("<H", cfg, 14, density)  # density
    return bytes(cfg)


def build(package_name="io.github.mcool.luotong",
          type_name="mipmap",
          entry_name="ic_launcher",
          package_id=0x7F):
    # 全局字符串池：每个密度一条 png 路径
    paths = ["res/mipmap-%s/ic_launcher.png" % name for name, _ in DENSITIES]
    gp = string_pool(paths)
    tp = string_pool([type_name])
    kp = string_pool([entry_name])

    entry_count = 1

    # ---- TypeSpec ----
    type_spec = bytearray()
    ts_size = 16 + 4 * entry_count
    type_spec += struct.pack("<HHI", RES_TABLE_TYPE_SPEC, 16, ts_size)
    type_spec += struct.pack("<BBHI", 1, 0, 0, entry_count)
    type_spec += struct.pack("<I", 0)

    # ---- 每个密度一个 Type chunk ----
    types = bytearray()
    for idx, (_name, dpi) in enumerate(DENSITIES):
        config = make_config(dpi)
        header_size = 20 + len(config)
        entries_start = header_size + 4 * entry_count
        entry = struct.pack("<HHI", 8, 0, 0)          # size, flags, key index
        entry += struct.pack("<HBBI", 8, 0, TYPE_STRING, idx)  # 指向全局池第 idx 项
        type_size = entries_start + len(entry)
        typ = bytearray()
        typ += struct.pack("<HHI", RES_TABLE_TYPE, header_size, type_size)
        typ += struct.pack("<BBHII", 1, 0, 0, entry_count, entries_start)
        typ += config
        typ += struct.pack("<I", 0)                   # 第 0 项偏移
        typ += entry
        types += typ

    # ---- Package ----
    # ResTable_package 的 name 是 char16[128]，即 256 字节
    name_bytes = package_name.encode("utf-16-le")[:254].ljust(256, b"\x00")
    type_strings_off = 288
    key_strings_off = type_strings_off + len(tp)
    body = tp + kp + bytes(type_spec) + bytes(types)
    pkg_size = 288 + len(body)
    pkg = bytearray()
    pkg += struct.pack("<HHI", RES_TABLE_PACKAGE, 288, pkg_size)
    pkg += struct.pack("<I", package_id)
    pkg += name_bytes
    pkg += struct.pack("<IIIII", type_strings_off, 1, key_strings_off, 1, 0)
    pkg += body

    total = 12 + len(gp) + len(pkg)
    out = bytearray()
    out += struct.pack("<HHII", RES_TABLE, 12, total, 1)
    out += gp
    out += pkg
    return bytes(out)


if __name__ == "__main__":
    data = build()
    open("/tmp/apk/out/resources.arsc", "wb").write(data)
    print("resources.arsc:", len(data), "bytes,", len(DENSITIES), "种密度")
