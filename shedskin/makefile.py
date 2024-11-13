# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.makefile: makefile generator"""

import os
import pathlib
import re
import subprocess
import sys
import sysconfig

# type-checking
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from . import config


def check_output(cmd: str) -> Optional[str]:
    """Run a command and return the output"""
    try:
        return subprocess.check_output(cmd.split(), encoding="utf8").strip()
    except FileNotFoundError:
        return None


def generate_makefile(gx: "config.GlobalInfo") -> None:
    """Generate a makefile"""
    if gx.nomakefile:
        return
    if sys.platform == "win32":
        pyver = "%d%d" % sys.version_info[:2]
        prefix = sysconfig.get_config_var("prefix")
    else:
        pyver = sysconfig.get_config_var("VERSION") or sysconfig.get_python_version()
        includes = "-I" + (sysconfig.get_config_var("INCLUDEPY") or "") + " "

        includes += "-I" + os.path.dirname(sysconfig.get_config_h_filename())

        if sys.platform == "darwin":
            ldflags = sysconfig.get_config_var("BASECFLAGS")
        else:
            ldflags = (sysconfig.get_config_var("LIBS") or "") + " "
            ldflags += (sysconfig.get_config_var("SYSLIBS") or "") + " "
            ldflags += "-lpython" + pyver
            if not sysconfig.get_config_var("Py_ENABLE_SHARED"):
                ldflags += " -L" + (sysconfig.get_config_var("LIBPL") or "")

    ident = gx.main_module.ident
    if gx.pyextension_product:
        if sys.platform == "win32":
            ident += ".pyd"
        else:
            ident += ".so"

    if gx.outputdir:
        makefile_path = os.path.join(gx.outputdir, gx.makefile_name)
    else:
        makefile_path = gx.makefile_name

    makefile = open(makefile_path, "w")

    def write(line: str = "") -> None:
        print(line, file=makefile)

    esc_space = r"\ "

    def env_var(name: str) -> str:
        return "${%s}" % name

    libdirs = [d.replace(" ", esc_space) for d in gx.libdirs]
    write("SHEDSKIN_LIBDIR=%s" % (libdirs[-1]))
    filenames = []
    modules = gx.modules.values()
    for module in modules:
        filename = os.path.splitext(module.filename)[0]  # strip .py
        filename = filename.replace(" ", esc_space)  # make paths valid
        if gx.outputdir and not module.builtin:
            filename = os.path.abspath(
                os.path.join(gx.outputdir, os.path.basename(filename))
            )
        else:
            filename = filename.replace(libdirs[-1], env_var("SHEDSKIN_LIBDIR"))
        filenames.append(filename)

    cppfiles = [fn + ".cpp" for fn in filenames]
    hppfiles = [fn + ".hpp" for fn in filenames]
    # used to be 're', but currently unused, but kept around just in case
    # for always in ():
    #        repath = os.path.join(env_var("SHEDSKIN_LIBDIR"), always)
    #        if repath not in filenames:
    #            cppfiles.append(repath + ".cpp")
    #            hppfiles.append(repath + ".hpp")

    cppfiles.sort(reverse=True)
    hppfiles.sort(reverse=True)
    cppfiles_str = " \\\n\t".join(cppfiles)
    hppfiles_str = " \\\n\t".join(hppfiles)

    # import flags
    if gx.flags:
        flags = gx.flags
    elif os.path.isfile("FLAGS"):
        flags = pathlib.Path("FLAGS")
    elif os.path.isfile("/etc/shedskin/FLAGS"):
        flags = pathlib.Path("/etc/shedskin/FLAGS")
    elif sys.platform == "win32":
        flags = gx.shedskin_flags / "FLAGS.mingw"
    elif sys.platform == "darwin":
        flags = gx.shedskin_flags / "FLAGS.osx"
    else:
        flags = gx.shedskin_flags / "FLAGS"

    line = ""
    for line in open(flags):
        line = line[:-1]

        variable = line[: line.find("=")].strip().rstrip("?")

        if variable == "CXXFLAGS":
            line += " -I. -I%s" % env_var("SHEDSKIN_LIBDIR")
            line += "".join(" -I" + libdir for libdir in libdirs[:-1])
            if sys.platform == "darwin" and os.path.isdir("/usr/local/include"):
                line += " -I/usr/local/include"  # XXX
            if sys.platform == "darwin" and os.path.isdir("/opt/local/include"):
                line += " -I/opt/local/include"  # XXX
            if not gx.wrap_around_check:
                line += " -D__SS_NOWRAP"
            if not gx.bounds_checking:
                line += " -D__SS_NOBOUNDS"
            if not gx.assertions:
                line += " -D__SS_NOASSERT"
            if gx.int32:
                line += " -D__SS_INT32"
            if gx.int64:
                line += " -D__SS_INT64"
            if gx.int128:
                line += " -D__SS_INT128"
            if gx.float32:
                line += " -D__SS_FLOAT32"
            if gx.float64:
                line += " -D__SS_FLOAT64"
            if gx.backtrace:
                line += " -D__SS_BACKTRACE -rdynamic -fno-inline"
            if gx.nogc:
                line += " -D__SS_NOGC"
            if gx.pyextension_product:
                if sys.platform == "win32":
                    line += " -I%s\\include -D__SS_BIND" % prefix
                else:
                    line += " -g -fPIC -D__SS_BIND " + includes

        elif variable == "LFLAGS":
            if sys.platform == "darwin" and os.path.isdir("/opt/local/lib"):  # XXX
                line += " -L/opt/local/lib"
            if sys.platform == "darwin" and os.path.isdir("/usr/local/lib"):  # XXX
                line += " -L/usr/local/lib"
            if gx.pyextension_product:
                if sys.platform == "win32":
                    line += " -shared -L%s\\libs -lpython%s" % (prefix, pyver)
                elif sys.platform == "darwin":
                    line += " -bundle -undefined dynamic_lookup " + ldflags
                elif sys.platform == "sunos5":
                    line += " -shared -Xlinker " + ldflags
                else:
                    line += " -Wno-register -shared -Xlinker -export-dynamic " + ldflags

            if "re" in [m.ident for m in modules]:
                line += " -lpcre"
            if "socket" in (m.ident for m in modules):
                if sys.platform == "win32":
                    line += " -lws2_32"
                elif sys.platform == "sunos5":
                    line += " -lsocket -lnsl"
            if "os" in (m.ident for m in modules):
                if sys.platform not in ["win32", "darwin", "sunos5"]:
                    line += " -lutil"
            if "hashlib" in (m.ident for m in modules):
                line += " -lcrypto"

        write(line)
    write()

    write("CPPFILES=%s\n" % cppfiles_str)
    write("HPPFILES=%s\n" % hppfiles_str)

    # tests for static
    MATCH = re.match(r"^LFLAGS=(.+)(\$\(LDFLAGS\).+)", line)
    HOMEBREW = check_output("brew --prefix")
    if sys.platform == "darwin" and HOMEBREW and MATCH:
        write("STATIC_PREFIX=$(shell brew --prefix)")
        write("STATIC_LIBDIR=$(STATIC_PREFIX)/lib")
        write("STATIC_INCLUDE=$(STATIC_PREFIX)/include")
        write()
        write("GC_STATIC=$(STATIC_LIBDIR)/libgc.a")
        write("GCCPP_STATIC=$(STATIC_LIBDIR)/libgccpp.a")
        write("GC_INCLUDE=$(STATIC_INCLUDE)/include")
        write("PCRE_STATIC=$(STATIC_LIBDIR)/libpcre.a")
        write("PCRE_INCLUDE=$(STATIC_INCLUDE)/include")
        write()
        write("STATIC_LIBS=$(GC_STATIC) $(GCCPP_STATIC) $(PCRE_STATIC)")
        write("STATIC_CXXFLAGS=$(CXXFLAGS) -I$(GC_INCLUDE) -I$(PCRE_INCLUDE)")
        write("STATIC_LFLAGS=" + MATCH.group(2))
        write()

    write("all:\t" + ident + "\n")

    # executable (normal, debug, profile) or extension module
    _out = "-o "
    _ext = ""
    targets = [("", "")]
    if not gx.pyextension_product:
        targets += [("_prof", "-pg -ggdb"), ("_debug", "-g -ggdb")]

    for suffix, options in targets:
        write(ident + suffix + ":\t$(CPPFILES) $(HPPFILES)")
        write(
            "\t$(CXX) "
            + options
            + " $(CXXFLAGS) $(CPPFILES) $(LFLAGS) "
            + _out
            + ident
            + suffix
            + _ext
            + "\n"
        )

    if sys.platform == "darwin" and HOMEBREW and MATCH:
        # static option
        write("static: $(CPPFILES) $(HPPFILES)")
        write(
            f"\t$(CXX) $(STATIC_CXXFLAGS) $(CPPFILES) $(STATIC_LIBS) $(STATIC_LFLAGS) -o {ident}\n"
        )

    # clean
    ext = ""
    if sys.platform == "win32" and not gx.pyextension_product:
        ext = ".exe"
    write("clean:")
    _targets = [ident + ext]
    if not gx.pyextension_product:
        _targets += [ident + "_prof" + ext, ident + "_debug" + ext]
    write("\trm -f %s" % " ".join(_targets))
    if sys.platform == "darwin":
        write("\trm -rf %s.dSYM\n" % " ".join(_targets))
    write()

    # phony
    phony = ".PHONY: all clean"
    if sys.platform == "darwin" and HOMEBREW and MATCH:
        phony += " static"
    phony += "\n"
    write(phony)
    makefile.close()
