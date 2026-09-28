"""List symbols from a game's shipped PDB with Windows' own dbghelp, no game running.

llvm-pdbutil refuses Bulletstorm's 125 MB PDB ("Too many directory blocks"); dbghelp reads it.
Usage: python pdb_symbols.py <exe> <mask> [<mask> ...]    e.g.  "*CalcSceneView*"  "*Stereo*"
Prints RVA (offset from the image base), size, and the symbol name.
"""
import ctypes
import ctypes.wintypes as wt
import os
import sys

dbghelp = ctypes.WinDLL("dbghelp")
MAX_NAME = 1024


class SYMBOL_INFO(ctypes.Structure):
    _fields_ = [("SizeOfStruct", wt.ULONG), ("TypeIndex", wt.ULONG), ("Reserved", ctypes.c_uint64 * 2),
                ("Index", wt.ULONG), ("Size", wt.ULONG), ("ModBase", ctypes.c_uint64),
                ("Flags", wt.ULONG), ("Value", ctypes.c_uint64), ("Address", ctypes.c_uint64),
                ("Register", wt.ULONG), ("Scope", wt.ULONG), ("Tag", wt.ULONG),
                ("NameLen", wt.ULONG), ("MaxNameLen", wt.ULONG), ("Name", ctypes.c_char * MAX_NAME)]


CALLBACK = ctypes.WINFUNCTYPE(wt.BOOL, ctypes.POINTER(SYMBOL_INFO), wt.ULONG, ctypes.c_void_p)
BASE = 0x10000000  # a fake load address; RVAs are printed relative to it


def main():
    exe, masks = os.path.abspath(sys.argv[1]), sys.argv[2:]
    proc = wt.HANDLE(0x1234)
    dbghelp.SymSetOptions(0x2 | 0x4)  # SYMOPT_UNDNAME | SYMOPT_DEFERRED_LOADS
    if not dbghelp.SymInitialize(proc, os.path.dirname(exe).encode(), False):
        raise SystemExit("SymInitialize failed")
    dbghelp.SymLoadModuleEx.restype = ctypes.c_uint64
    base = dbghelp.SymLoadModuleEx(proc, None, exe.encode(), None, ctypes.c_uint64(BASE), 0, None, 0)
    if not base:
        raise SystemExit("SymLoadModuleEx failed")
    rows = []

    def cb(info, size, ctx):
        s = info.contents
        rows.append((s.Address - base, s.Size, s.Name.decode("latin-1")))
        return True

    c = CALLBACK(cb)
    for m in masks:
        dbghelp.SymEnumSymbols(proc, ctypes.c_uint64(base), m.encode(), c, None)
    for rva, size, name in sorted(set(rows), key=lambda r: r[2]):
        print(f"{rva:#010x} {size:6d} {name}")
    dbghelp.SymCleanup(proc)


if __name__ == "__main__":
    main()
