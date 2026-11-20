"""Read the Intel driver's global and CS2 settings using IGCL get calls."""
import ctypes as c
import os
from pathlib import Path

U32 = c.c_uint32
Ptr = c.c_void_p


class Init(c.Structure):
    _fields_ = [("size", U32), ("version", c.c_uint8), ("app_version", U32),
                ("flags", U32), ("driver_version", U32), ("uid", U32 * 4)]


class Feature(c.Structure):
    _fields_ = [("size", U32), ("version", c.c_uint8), ("feature", U32),
                ("app_name", c.c_char_p), ("name_length", c.c_int8),
                ("set", c.c_bool), ("value_type", U32), ("value", U32 * 2),
                ("custom_size", c.c_int32), ("custom", Ptr)]


dll = c.CDLL(str(Path(os.environ["SystemRoot"]) / "System32" / "ControlLib.dll"))
def bind(name, *args):
    func = getattr(dll, name)
    func.argtypes = args
    func.restype = U32
    return func


def checked(result):
    if result:
        raise RuntimeError(f"IGCL result {result:#010x}")


init = bind("ctlInit", c.POINTER(Init), c.POINTER(Ptr))
enum = bind("ctlEnumerateDevices", Ptr, c.POINTER(U32), c.POINTER(Ptr))
read = bind("ctlGetSet3DFeature", Ptr, c.POINTER(Feature))
close = bind("ctlClose", Ptr)
args = Init(size=c.sizeof(Init), app_version=0x10001)
handle = Ptr()
checked(init(c.byref(args), c.byref(handle)))
try:
    count = U32()
    checked(enum(handle, c.byref(count), None))
    devices = (Ptr * count.value)()
    checked(enum(handle, c.byref(count), devices))
    print(f"Intel adapters={count.value}, IGCL={args.driver_version:#x}")
    for device in devices:
        for name in [None, b"cs2.exe"]:
            for key, feature_id, kind in [("frame_limit", 2, 2), ("flip_mode", 9, 4),
                                          ("frame_pacing", 0, 4), ("low_latency", 16, 4)]:
                query = Feature(size=c.sizeof(Feature), feature=feature_id, app_name=name,
                                name_length=len(name or b""), value_type=kind)
                result = read(device, c.byref(query))
                print((name or b"global").decode(), key, f"result={result:#010x}",
                      f"raw={list(query.value)}" if result == 0 else "")
finally:
    close(handle)
