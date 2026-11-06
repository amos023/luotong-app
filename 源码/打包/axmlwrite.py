"""把简单的 XML 树编码为 Android 二进制 AXML（AndroidManifest.xml）。

要点：属性名必须排在字符串池最前，并配套等长的 resource map，
否则系统的 PackageParser 拿不到 android:xxx 的资源 ID，安装会失败。
属性名 → 资源 ID 的取值已用真机 APK 反查确认（见 axml_probe.py 输出）。
"""
import struct

ANDROID_NS = "http://schemas.android.com/apk/res/android"

RID = {
    "theme": 0x01010000,
    "label": 0x01010001,
    "icon": 0x01010002,
    "name": 0x01010003,
    "exported": 0x01010010,
    "configChanges": 0x0101001f,
    "minSdkVersion": 0x0101020c,
    "versionCode": 0x0101021b,
    "versionName": 0x0101021c,
    "targetSdkVersion": 0x01010270,
    "allowBackup": 0x01010280,
    "hardwareAccelerated": 0x010102d3,
    "usesCleartextTraffic": 0x010104ec,
}

T_STRING, T_REF, T_INT, T_BOOL = 0x03, 0x01, 0x10, 0x12


class El:
    """一个元素：tag、属性表、子元素。属性表项为 (是否 android 命名空间, 名字, 类型, 值)。"""

    def __init__(self, tag, attrs=(), children=()):
        self.tag = tag
        self.attrs = list(attrs)
        self.children = list(children)


def _chrome():
    """按层级写出（namespace 开始/结束由调用方处理）。"""
    pass


class Writer:
    def __init__(self, root):
        self.root = root
        self.pool = []
        self.pindex = {}
        self.body = bytearray()
        self.attr_order = []

    # ---------- 字符串池 ----------
    def si(self, s):
        if s in self.pindex:
            return self.pindex[s]
        self.pindex[s] = len(self.pool)
        self.pool.append(s)
        return self.pindex[s]

    def collect_attr_names(self, el):
        for is_android, name, typ, val in el.attrs:
            if name not in self.attr_order:
                self.attr_order.append(name)
        for ch in el.children:
            self.collect_attr_names(ch)

    # ---------- 编码 ----------
    def encode(self):
        self.collect_attr_names(self.root)
        # 属性名先入池，保证 resmap 连续覆盖前 N 项
        for name in self.attr_order:
            self.si(name)
        self.si("android")
        self.si(ANDROID_NS)

        self.emit_ns_start("android", ANDROID_NS)
        self.emit_el(self.root)
        self.emit_ns_end("android", ANDROID_NS)

        pool = self.build_pool()
        resmap = bytearray()
        ids = [RID.get(n, 0) for n in self.attr_order]
        if ids:
            resmap += struct.pack("<HHI", 0x0180, 8, 8 + 4 * len(ids))
            resmap += struct.pack("<%dI" % len(ids), *ids)
        total = 8 + len(pool) + len(resmap) + len(self.body)
        return struct.pack("<HHI", 0x0003, 8, total) + pool + bytes(resmap) + bytes(self.body)

    def emit_el(self, el):
        name = self.si(el.tag)
        blob = bytearray()
        for is_android, aname, typ, val in el.attrs:
            ans = self.si(ANDROID_NS) if is_android else 0xFFFFFFFF
            an = self.si(aname)
            # 单个属性 20 字节：ns(4) name(4) rawValue(4) + Res_value(8)
            if typ == T_STRING:
                raw = self.si(val)
                blob += struct.pack("<III", ans, an, raw) + struct.pack("<HBBI", 8, 0, T_STRING, raw)
            elif typ == T_REF:
                blob += struct.pack("<III", ans, an, 0xFFFFFFFF) + struct.pack("<HBBI", 8, 0, T_REF, val)
            elif typ == T_BOOL:
                blob += struct.pack("<III", ans, an, 0xFFFFFFFF) + struct.pack("<HBBI", 8, 0, T_BOOL, 0xFFFFFFFF if val else 0)
            else:
                blob += struct.pack("<III", ans, an, 0xFFFFFFFF) + struct.pack("<HBBI", 8, 0, T_INT, val)
        size = 16 + 20 + len(blob)
        self.body += struct.pack("<HHIII", 0x0102, 16, size, 0xFFFFFFFF, 0xFFFFFFFF)
        self.body += struct.pack("<IIHHHHHH", 0xFFFFFFFF, name, 20, 20, len(el.attrs), 0, 0, 0)
        self.body += blob
        for ch in el.children:
            self.emit_el(ch)
        self.body += struct.pack("<HHIII", 0x0103, 16, 24, 0xFFFFFFFF, 0xFFFFFFFF)
        self.body += struct.pack("<II", 0xFFFFFFFF, name)

    def emit_ns_start(self, prefix, uri):
        p, u = self.si(prefix), self.si(uri)
        self.body += struct.pack("<HHIII", 0x0100, 16, 24, 0xFFFFFFFF, 0xFFFFFFFF)
        self.body += struct.pack("<II", p, u)

    def emit_ns_end(self, prefix, uri):
        p, u = self.si(prefix), self.si(uri)
        self.body += struct.pack("<HHIII", 0x0101, 16, 24, 0xFFFFFFFF, 0xFFFFFFFF)
        self.body += struct.pack("<II", p, u)

    def build_pool(self):
        data = bytearray()
        offsets = []
        for s in self.pool:
            offsets.append(len(data))
            enc = s.encode("utf-16-le")
            data += struct.pack("<H", len(enc) // 2) + enc + b"\x00\x00"
        while len(data) % 4:
            data += b"\x00"
        count = len(self.pool)
        strings_start = 28 + 4 * count
        size = strings_start + len(data)
        out = bytearray()
        out += struct.pack("<HHI", 0x0001, 28, size)
        out += struct.pack("<IIIII", count, 0, 0, strings_start, 0)
        if count:
            out += struct.pack("<%dI" % count, *offsets)
        out += data
        return bytes(out)


def build_manifest(package, version_code, version_name, label, activity_class,
                   min_sdk=21, target_sdk=34, config_changes=0x0DB0, icon_rid=None):
    act = El("activity", [
        (True, "name", T_STRING, activity_class),
        (True, "exported", T_BOOL, True),
        (True, "label", T_STRING, label),
        (True, "configChanges", T_INT, config_changes),
    ], [
        El("intent-filter", [
            (True, "label", T_STRING, label),
        ], [
            El("action", [(True, "name", T_STRING, "android.intent.action.MAIN")]),
            El("category", [(True, "name", T_STRING, "android.intent.category.LAUNCHER")]),
        ]),
    ])
    app_attrs = [(True, "label", T_STRING, label)]
    if icon_rid is not None:
        app_attrs.append((True, "icon", T_REF, icon_rid))
    app = El("application", app_attrs + [
        (True, "allowBackup", T_BOOL, True),
        (True, "hardwareAccelerated", T_BOOL, True),
        (True, "usesCleartextTraffic", T_BOOL, True),
    ], [act])
    uses_sdk = El("uses-sdk", [
        (True, "minSdkVersion", T_INT, min_sdk),
        (True, "targetSdkVersion", T_INT, target_sdk),
    ])
    manifest = El("manifest", [
        (False, "package", T_STRING, package),
        (True, "versionCode", T_INT, version_code),
        (True, "versionName", T_STRING, version_name),
    ], [uses_sdk, app])
    return Writer(manifest).encode()
