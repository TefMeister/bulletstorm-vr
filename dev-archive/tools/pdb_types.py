"""pdb_types.py - list a struct/class's data members (name, byte offset, size) from a game's shipped PDB.

Companion to pdb_symbols.py (same dbghelp approach; llvm-pdbutil cannot open a PDB this large). Reads files only;
never touches a running game.

Usage: python pdb_types.py <exe> <TypeName> [<TypeName> ...]     e.g.  FSceneView  FViewInfo
"""
import ctypes
import ctypes.wintypes as wt
import os
import sys

dbghelp = ctypes.WinDLL("dbghelp")
MAX_NAME = 2000
BASE = 0x10000000           # a fake load address, as in pdb_symbols.py
FAKE_PROCESS = 0x1235       # dbghelp only needs a unique handle value, not a real process

# IMAGEHLP_SYMBOL_TYPE_INFO values (dbghelp.h)
TI_GET_SYMTAG, TI_GET_SYMNAME, TI_GET_LENGTH, TI_GET_TYPE = 0, 1, 2, 4
TI_GET_TYPEID, TI_GET_OFFSET, TI_GET_CHILDRENCOUNT, TI_FINDCHILDREN = 5, 10, 13, 7
SYMTAG_DATA, SYMTAG_BASECLASS = 7, 18


class SYMBOL_INFO(ctypes.Structure):
    _fields_ = [("SizeOfStruct", wt.ULONG), ("TypeIndex", wt.ULONG), ("Reserved", ctypes.c_uint64 * 2),
                ("Index", wt.ULONG), ("Size", wt.ULONG), ("ModBase", ctypes.c_uint64),
                ("Flags", wt.ULONG), ("Value", ctypes.c_uint64), ("Address", ctypes.c_uint64),
                ("Register", wt.ULONG), ("Scope", wt.ULONG), ("Tag", wt.ULONG),
                ("NameLen", wt.ULONG), ("MaxNameLen", wt.ULONG), ("Name", ctypes.c_char * MAX_NAME)]


def info(proc, base, type_id, what, out):
    return dbghelp.SymGetTypeInfo(proc, ctypes.c_uint64(base), type_id, what, ctypes.byref(out))


def name_of(proc, base, type_id):
    p = ctypes.c_wchar_p()
    if not dbghelp.SymGetTypeInfo(proc, ctypes.c_uint64(base), type_id, TI_GET_SYMNAME, ctypes.byref(p)):
        return "?"
    s = p.value
    ctypes.windll.kernel32.LocalFree(p)
    return s


def type_name(proc, base, type_id):
    t = wt.DWORD()
    if not info(proc, base, type_id, TI_GET_TYPE, t):
        return ""
    n = name_of(proc, base, t.value)
    return n if n != "?" else ""


def members(proc, base, type_id):
    count = wt.DWORD()
    if not info(proc, base, type_id, TI_GET_CHILDRENCOUNT, count) or not count.value:
        return []

    class FIND(ctypes.Structure):
        _fields_ = [("Count", wt.ULONG), ("Start", wt.ULONG), ("ChildId", wt.ULONG * count.value)]

    f = FIND(count.value, 0)
    if not dbghelp.SymGetTypeInfo(proc, ctypes.c_uint64(base), type_id, TI_FINDCHILDREN, ctypes.byref(f)):
        return []
    rows = []
    for child in f.ChildId:
        tag, off, length, t = wt.DWORD(), wt.DWORD(), ctypes.c_uint64(), wt.DWORD()
        info(proc, base, child, TI_GET_SYMTAG, tag)
        if tag.value not in (SYMTAG_DATA, SYMTAG_BASECLASS):
            continue
        if not info(proc, base, child, TI_GET_OFFSET, off):
            continue                                           # static member
        info(proc, base, child, TI_GET_TYPE, t)
        info(proc, base, t.value, TI_GET_LENGTH, length)
        label = name_of(proc, base, child) if tag.value == SYMTAG_DATA else "(base) " + name_of(proc, base, t.value)
        rows.append((off.value, length.value, label, type_name(proc, base, child)))
    return sorted(rows)


def main():
    exe, names = os.path.abspath(sys.argv[1]), sys.argv[2:]
    proc = wt.HANDLE(FAKE_PROCESS)
    dbghelp.SymSetOptions(0x2 | 0x4)
    if not dbghelp.SymInitialize(proc, os.path.dirname(exe).encode(), False):
        raise SystemExit("SymInitialize failed")
    dbghelp.SymLoadModuleEx.restype = ctypes.c_uint64
    base = dbghelp.SymLoadModuleEx(proc, None, exe.encode(), None, ctypes.c_uint64(BASE), 0, None, 0)
    if not base:
        raise SystemExit("SymLoadModuleEx failed")
    for n in names:
        s = SYMBOL_INFO()
        s.SizeOfStruct = ctypes.sizeof(SYMBOL_INFO) - MAX_NAME
        s.MaxNameLen = MAX_NAME
        if not dbghelp.SymGetTypeFromName(proc, ctypes.c_uint64(base), n.encode(), ctypes.byref(s)):
            print(f"== {n}: not found")
            continue
        size = ctypes.c_uint64()
        info(proc, base, s.TypeIndex, TI_GET_LENGTH, size)
        print(f"== {n} ({size.value} bytes)")
        for off, length, label, tname in members(proc, base, s.TypeIndex):
            print(f"  +{off:#06x} {length:5d}  {label}" + (f"  : {tname}" if tname else ""))
    dbghelp.SymCleanup(proc)


if __name__ == "__main__":
    main()
