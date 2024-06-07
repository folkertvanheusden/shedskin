"""
*** SHED SKIN Python-to-C++ Compiler ***

Copyright 2005-2023 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)

cmake support contributed by Shakeeb Alireza
License GNU GPL version 3 (See LICENSE)

shedskin cmake builder

api:

    shedskin build app.py
    shedskin build pkg/app.py

"""
import argparse
import glob
import logging
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import textwrap
import time

from . import config

from .utils import CYAN, GREEN, RED, RESET, WHITE

from typing import Optional, Union

# type alias
Pathlike = Union[pathlib.Path, str]

def get_pkg_path() -> pathlib.Path:
    """return shedskin package path"""
    _pkg_path = pathlib.Path(__file__).parent
    assert _pkg_path.name == "shedskin"
    return _pkg_path

def pkg_path():
    """used by cmake to get package path automatically"""
    sys.stdout.write(str(get_pkg_path()))

def get_user_cache_dir():
    """get user cache directory dependending on platform"""
    system = platform.system()
    if system == "Darwin":
        return pathlib.Path("~/Library/Caches/shedskin").expanduser()
    elif system == "Linux":
        return pathlib.Path("~/.cache/shedskin").expanduser()
    elif system == "Windows":
        profile = os.getenv("USERPROFILE")
        if not profile:
            raise SystemExit(f"USERPROFILE environment variable not set on windows")
        user_dir = pathlib.Path(profile)
        return user_dir / 'AppData' / 'Local' / 'shedskin' / 'Cache'
    else:
        raise SystemExit(f"{system} os not supported")

def user_cache_dir():
    """used by CMakeLists.txt execute process"""
    sys.stdout.write(str(get_user_cache_dir()))


class ConanBDWGC:
    """conan gc dependency"""

    def __init__(
        self,
        name: str = "bdwgc",
        version: str  = "8.2.2",
        cplusplus: bool = True,
        cord: bool = False,
        gcj_support: bool = False,
        java_finalization: bool = False,
        shared: bool = False,
    ):
        self.name = name
        self.version = version
        self.cplusplus = cplusplus
        self.cord = cord
        self.gcj_support = gcj_support
        self.java_finalization = java_finalization
        self.shared = shared

    def __str__(self):
        return f"{self.name}/{self.version}"


class ConanPCRE:
    """conan pcre dependency"""

    def __init__(
        self,
        name: str = "pcre",
        version: str ="8.45",
        build_pcrecpp: bool = True,
        build_pcregrep: bool =False,
        shared: bool =False,
        with_bzip2: bool =False,
        with_zlib: bool =False,
    ):
        self.name = name
        self.version = version
        self.build_pcrecpp = build_pcrecpp
        self.build_pcregrep = build_pcregrep
        self.shared = shared
        self.with_bzip2 = with_bzip2
        self.with_zlib = with_zlib

    def __str__(self):
        return f"{self.name}/{self.version}"

class ConanDependencyManager:
    """dep manager which manages and install all conan dependencies"""

    def __init__(self, source_dir: Pathlike):
        self.source_dir = pathlib.Path(source_dir)
        self.build_dir = self.source_dir / "build"
        self.bdwgc = ConanBDWGC()
        self.pcre = ConanPCRE()

    def generate_conanfile(self):
        """generate conanfile file"""
        bdwgc = self.bdwgc
        pcre = self.pcre
        content = textwrap.dedent(
            f"""
        [requires]
        {bdwgc}
        {pcre}

        [generators]
        cmake_find_package
        cmake_paths

        [options]
        bdwgc:cplusplus={bdwgc.cplusplus}
        bdwgc:cord={bdwgc.cord}
        bdwgc:gcj_support={bdwgc.gcj_support}
        bdwgc:java_finalization={bdwgc.java_finalization}
        bdwgc:shared={bdwgc.shared}
        pcre:build_pcrecpp={pcre.build_pcrecpp}
        pcre:build_pcregrep={pcre.build_pcregrep}
        pcre:shared={pcre.shared}
        pcre:with_bzip2={pcre.with_bzip2}
        pcre:with_zlib={pcre.with_zlib}
        """
        )
        conanfile = self.source_dir / "conanfile.txt"
        if not conanfile.exists():
            conanfile.write_text(content)

    def install(self):
        """install conan dependencies"""
        os.system(f"cd {self.build_dir} && conan install .. --build=missing")


class ShedskinDependencyManager:
    """shedskin local dependency manager (SPM) class"""

    def __init__(self, source_dir: Pathlike, reset_on_run: bool = False):
        self.reset_on_run = reset_on_run
        self.source_dir = pathlib.Path(source_dir)
        self.build_dir = self.source_dir / "build"
        # self.deps_dir = self.build_dir / "deps"
        self.deps_dir = get_user_cache_dir()
        # self.deps_dir = pathlib.Path.home() / ".cache" / "shedskin"
        self.include_dir = self.deps_dir / "include"
        self.lib_dir = self.deps_dir / "lib"
        self.downloads_dir = self.deps_dir / "downloads"
        self.src_dir = self.deps_dir / "src"
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.lib_suffix = ".lib" if sys.platform == "win32" else ".a"

        if self.reset_on_run:
            shutil.rmtree(self.deps_dir)

    def shellcmd(self, cmd: str, *args, **kwds):
        """run shellcmd"""
        print("-" * 80)
        print(f"{WHITE}cmd{RESET}: {CYAN}{cmd}{RESET}")
        os.system(cmd.format(*args, **kwds))

    def git_clone(self, repo: str, to_dir: str, branch: Optional[str] = None):
        """retrieve git clone of repo"""
        if branch:
          self.shellcmd(f"git clone -b {branch} --depth=1 {repo} {to_dir}")
        else:
           self.shellcmd(f"git clone --depth=1 {repo} {to_dir}")

    def cmake_generate(self, src_dir: Pathlike, build_dir: Pathlike, prefix: Pathlike, **options):
        """activate cmake configuration / generation stage"""
        opts = " ".join(f"-D{k}={v}" for k, v in options.items())
        self.shellcmd(
            f"cmake -S {src_dir} -B {build_dir} --install-prefix {prefix} {opts}"
        )

    def cmake_build(self, build_dir: Pathlike, release: bool = True):
        """activate cmake build stage"""
        if release:
            build_type = "Release"
        else:
            build_type = "Debug"
        self.shellcmd(f"cmake --build {build_dir} --config {build_type}")

    def cmake_install(self, build_dir: Pathlike):
        """activate cmake install stage"""
        self.shellcmd(f"cmake --install {build_dir}")

    def wget(self, url: str, output_dir: Pathlike):
        """download url resource using wget"""
        self.shellcmd(f"wget -P {output_dir} {url}")

    def tar(self, archive: Pathlike, output_dir: Pathlike):
        """uncompress tar archive"""
        self.shellcmd(f"tar -xvf {archive} -C {output_dir}")

    def targets_exist(self) -> bool:
        """check if required targets exist"""
        libgc = self.lib_dir / f"libgc{self.lib_suffix}"
        libgccpp = self.lib_dir / f"libgccpp{self.lib_suffix}"
        libpcre = self.lib_dir / f"libgccpp{self.lib_suffix}"
        gc_h = self.include_dir / "gc.h"
        pcre_h = self.include_dir / "pcre.h"

        targets = [libgc, libgccpp, libpcre, gc_h, pcre_h]
        return all(t.exists() for t in targets)

    def install_all(self):
        """install all dependencies"""
        if not self.targets_exist():
            self.install_bdwgc()
            self.install_pcre()
        else:
            print(f"{WHITE}SPM:{RESET} targets exist, no need to run.")

    # def install_libatomics_ops(self):
    #     """install libatomic_ops, a bdwgc dependency on windws"""
    #     libatomic_repo = "https://github.com/ivmai/libatomic_ops.git"
    #     libatomic_src = self.src_dir / "libatomic_ops"
    #     libatomic_build = libatomic_src / "build"
    #     print("download / build / install libatomic_ops")
    #     self.git_clone(libatomic_repo, libatomic_src, branch="v7.8.2")
    #     libatomic_build.mkdir(exist_ok=True)
    #     self.cmake_generate(
    #         libatomic_src,
    #         libatomic_build,
    #         enable_atomic_intrinsics=False,
    #         prefix=self.deps_dir,
    #         BUILD_SHARED_LIBS=False,
    #     )
    #     self.cmake_build(libatomic_build)
    #     self.cmake_install(libatomic_build)

    def install_bdwgc(self):
        """download / build / install bdwgc"""
        # if platform.system() == "Windows":
        #     self.install_libatomics_ops()
        bdwgc_repo = "https://github.com/ivmai/bdwgc"
        bdwgc_src = self.src_dir / "bdwgc"
        bdwgc_build = bdwgc_src / "build"

        print("download / build / install bdwgc")
        self.git_clone(bdwgc_repo, bdwgc_src)
        if platform.system() == "Windows":
            # windows needs libatomic_ops
            libatomic_repo = "https://github.com/ivmai/libatomic_ops.git"
            libatomic_src = bdwgc_src / "libatomic_ops"
            self.git_clone(libatomic_repo, libatomic_src)
        bdwgc_build.mkdir(exist_ok=True)
        self.cmake_generate(
            bdwgc_src,
            bdwgc_build,
            prefix=self.deps_dir,
            BUILD_SHARED_LIBS=False,
            enable_cplusplus=True,
            build_cord=False,
            enable_docs=False,
            enable_gcj_support=False,
            enable_java_finalization=False,
        )
        self.cmake_build(bdwgc_build)
        self.cmake_install(bdwgc_build)

    # def install_pcre(self):
    #         """download / build / install pcre"""
    #         pcre_url = (
    #             "https://sourceforge.net/projects/pcre/files/pcre/8.45/pcre-8.45.tar.gz"
    #         )
    #         pcre_archive = self.downloads_dir / "pcre-8.45.tar.gz"
    #         pcre_src = self.src_dir / "pcre-8.45"
    #         pcre_build = pcre_src / "build"

    #         print("download / build / install pcre")
    #         self.wget(pcre_url, self.downloads_dir)
    #         self.tar(pcre_archive, self.src_dir)
    #         # pcre_archive.unlink()
    #         pcre_build.mkdir(parents=True, exist_ok=True)
    #         self.cmake_generate(
    #             pcre_src,
    #             pcre_build,
    #             prefix=self.deps_dir,
    #             BUILD_SHARED_LIBS=False,
    #             PCRE_BUILD_PCREGREP=False,
    #             PCRE_BUILD_PCRECPP=True,
    #             PCRE_SUPPORT_LIBREADLINE=False,
    #             PCRE_SUPPORT_LIBEDIT=False,
    #             PCRE_SUPPORT_LIBZ=False,
    #             PCRE_SUPPORT_LIBBZ2=False,
    #             PCRE_BUILD_TESTS=False,
    #             PCRE_SHOW_REPORT=False,
    #         )
    #         self.cmake_build(pcre_build)
    #         self.cmake_install(pcre_build)

    def install_pcre(self):
        """download / build / install pcre"""
        pcre_repo = "https://github.com/luvit/pcre.git"
        pcre_src = self.src_dir / 'pcre'
        pcre_build =  pcre_src / "build"
        print("download / build / install pcre")
        self.git_clone(pcre_repo, pcre_src)
        pcre_build.mkdir(parents=True, exist_ok=True)
        self.cmake_generate(
            pcre_src,
            pcre_build,
            prefix=self.deps_dir,
            BUILD_SHARED_LIBS=False,
            PCRE_BUILD_PCREGREP=False,
            PCRE_BUILD_PCRECPP=True,
            PCRE_SUPPORT_LIBREADLINE=False,
            PCRE_SUPPORT_LIBEDIT=False,
            PCRE_SUPPORT_LIBZ=False,
            PCRE_SUPPORT_LIBBZ2=False,
            PCRE_BUILD_TESTS=False,
            PCRE_SHOW_REPORT=False,
        )
        self.cmake_build(pcre_build)
        self.cmake_install(pcre_build)

def add_shedskin_product(
    main_module: Optional[str] = None,
    sys_modules: Optional[list[str]] = None,
    app_modules: Optional[list[str]] = None,
    data: Optional[list[str]] = None,
    include_dirs: Optional[list[str]] = None,
    link_libs: Optional[list[str]] = None,
    link_dirs: Optional[list[str]] = None,
    compile_options: Optional[str] = None,
    link_options: Optional[str] = None,
    cmdline_options: Optional[str] = None,
    build_executable: bool = False,
    build_extension: bool = False,
    build_test: bool = False,
    disable_executable: bool = False,
    disable_extension: bool = False,
    disable_test: bool = False,
    # has_lib: bool = False,
    enble_conan: bool = False,
    enable_externalproject: bool = False,
    enable_spm: bool = False,
    debug: bool = False,
    name: Optional[str] = None,
    extra_lib_dir: Optional[str] = None,
):
    """populates a cmake function with the same name

    boolean options:
        HAS_LIB
        DEBUG

    boolean option pairs (setting one unsets the other)
        BUILD_EXECUTABLE BUILD_EXTENSION BUILD_TEST
        DISABLE_EXECUTABLE DISABLE_EXTENSION DISABLE_TEST

    radio options (mutually exclusive):
        ENABLE_CONAN ENABLE_SPM ENABLE_EXTERNALPROJECT

    single_value options:
        NAME MAIN_MODULE

    multiple value options:
        SYS_MODULES APP_MODULES DATA
        INCLUDE_DIRS LINK_LIBS LINK_DIRS
        COMPILE_OPTIONS LINK_OPTIONS CMDLINE_OPTIONS
        EXTRA_LIB_DIRS
    """

    if extra_lib_dir:
        cmdline_options = '-X' + extra_lib_dir
        include_dirs = [extra_lib_dir]

    def mk_add(lines: list[str], spaces: int = 4):
        def _append(level, txt):
            indentation = " " * spaces * level
            lines.append(f"{indentation}{txt}")

        return _append

    flist = ["add_shedskin_product("]
    add = mk_add(flist)

    if build_executable:
        add(1, "BUILD_EXECUTABLE")
    if disable_executable:
        add(1, "DISABLE_EXECUTABLE")

    if build_extension:
        add(1, "BUILD_EXTENSION")
    if disable_extension:
        add(1, "DISABLE_EXTENSION")

    if build_test:
        add(1, "BUILD_TEST")
    if disable_test:
        add(1, "DISABLE_TEST")

    if enable_externalproject:
        add(1, "ENABLE_EXTERNALPROJECT")
    elif enble_conan:
        add(1, "ENABLE_CONAN")
    elif enable_spm:
        add(1, "ENABLE_SPM")

    if debug:
        add(1, "DEBUG")

    if name:
        add(1, f"NAME {name}")

    if main_module:
        add(1, f"MAIN_MODULE {main_module}")

    if extra_lib_dir:
        add(1, f"EXTRA_LIB_DIR {extra_lib_dir}")

    if include_dirs:
        add(1, "INCLUDE_DIRS")
        for include_dir in sorted(include_dirs):
            add(2, include_dir)

    if link_libs:
        add(1, "LINK_LIBS")
        for link_lib in sorted(link_libs):
            add(2, link_lib)

    if link_dirs:
        add(1, "LINK_DIRS")
        for link_dir in sorted(link_dirs):
            add(2, link_dir)

    if compile_options:
        add(1, f"COMPILE_OPTIONS {compile_options}")

    if link_options:
        add(1, f"LINK_OPTIONS {link_options}")

    if cmdline_options:
        add(1, f"CMDLINE_OPTIONS {cmdline_options}")

    if sys_modules:
        add(1, "SYS_MODULES")
        for sys_mod in sorted(sys_modules):
            add(2, sys_mod)

    if app_modules:
        add(1, "APP_MODULES")
        for app_mod in sorted(app_modules):
            add(2, app_mod)
    if data:
        add(1, "DATA")
        for elem in sorted(data):
            add(2, elem)

    add(0, ")")
    return "\n".join(flist)


def get_cmakefile_template(**kwds):
    """returns a cmake template"""
    _pkg_path = get_pkg_path()
    cmakelists_tmpl = _pkg_path / "resources" / "cmake" / "CMakeLists.txt"
    tmpl = cmakelists_tmpl.read_text()
    return tmpl % kwds

def check_cmake_availability():
    """check if cmake executable is available in path"""
    if not bool(shutil.which('cmake')):
        raise Exception("cmake not available in path")

def generate_cmakefile(gx: config.GlobalInfo):
    """improved generator using built-in machinery"""
    path = gx.main_module.filename

    in_source_build = bool(len(path.relative_to(gx.cwd).parts) == 1)

    modules = gx.modules.values()
    # filenames = [f'{m.filename.parent / m.filename.stem}' for m in modules]

    sys_mods = set()
    app_mods = set()

    compile_options = []
    if gx.int32:
        compile_options.append("-D__SS_INT32")
    if gx.int64:
        compile_options.append("-D__SS_INT64")
    if gx.int128:
        compile_options.append("-D__SS_INT128")
    if gx.float32:
        compile_options.append("-D__SS_FLOAT32")
    if gx.float64:
        compile_options.append("-D__SS_FLOAT64")
    if not gx.bounds_checking:
        compile_options.append("-D__SS_NOBOUNDS")
    if not gx.wrap_around_check:
        compile_options.append("-D__SS_NOWRAP")
    if gx.backtrace:
        compile_options.append("-D__SS_BACKTRACE -rdynamic -fno-inline")
    if not gx.assertions:
        compile_options.append("-D__SS_NOASSERT")
    if gx.backtrace:
        compile_options.append("-D__SS_BACKTRACE -rdynamic -fno-inline")
    if gx.nogc:
        compile_options.append("-D__SS_NOGC")
    compile_opts = ' '.join(compile_options)

    for module in modules:
        if module.builtin and module.filename.is_relative_to(gx.shedskin_lib):
            entry = module.filename.relative_to(gx.shedskin_lib)
            entry = entry.parent / entry.stem
            if entry.name == "builtin":  # don't include 'builtin' module
                continue
            sys_mods.add(entry.as_posix())
        else:
            if module.filename.is_relative_to(gx.main_module.filename.parent):
                entry = module.filename.relative_to(gx.main_module.filename.parent)
            else:
                entry = module.filename
            entry = entry.parent / entry.stem
            if entry.name == path.stem:  # don't include main_module
                continue
            app_mods.add(entry.as_posix())

    assert gx.options, "gx.options must be populated"
    if in_source_build:
        master_clfile = path.parent / "CMakeLists.txt"
        master_clfile_content = get_cmakefile_template(
            project_name=f"{gx.main_module.ident}_project",
            is_simple_project="ON",
            entry=add_shedskin_product(
                path.name,
                list(sys_mods),
                list(app_mods),
                name=path.stem,
                build_executable=gx.executable_product,
                build_extension=gx.pyextension_product,
                include_dirs=gx.options.include_dirs,
                link_dirs=gx.options.link_dirs,
                link_libs=gx.options.link_libs,
                extra_lib_dir=gx.options.extra_lib,
                compile_options=compile_opts,
            ),
        )
        master_clfile.write_text(master_clfile_content)

    else:
        src_clfile = path.parent / "CMakeLists.txt"

        src_clfile.write_text(
            add_shedskin_product(
                path.name,
                list(sys_mods),
                list(app_mods),
                build_executable=gx.executable_product,
                build_extension=gx.pyextension_product,
                include_dirs=gx.options.include_dirs,
                link_dirs=gx.options.link_dirs,
                link_libs=gx.options.link_libs,
                extra_lib_dir=gx.options.extra_lib,
                compile_options=compile_opts,
            )
        )

        master_clfile = src_clfile.parent.parent / "CMakeLists.txt"
        master_clfile_content = get_cmakefile_template(
            project_name=f"{gx.main_module.ident}_project",
            is_simple_project="OFF",
            entry=f"add_subdirectory({path.parent.name})",
        )
        master_clfile.write_text(master_clfile_content)


class CMakeBuilder:
    """shedskin cmake builder"""

    def __init__(self, options: argparse.Namespace):
        self.options = options
        if len(pathlib.Path(options.name).parts) == 1:
            self.source_dir = pathlib.Path.cwd()
            self.build_dir = self.source_dir / "build"
        else:
            self.source_dir = pathlib.Path.cwd().parent
            self.build_dir = self.source_dir / "build"
        self.tests = sorted(glob.glob("./test_*/test_*.py", recursive=True))
        self.log = logging.getLogger(self.__class__.__name__)

    def check(self, path: Pathlike):
        """check file for syntax errors"""
        with open(path, encoding="utf8") as fopen:
            src = fopen.read()
        compile(src, path, "exec")

    def get_most_recent_test(self):
        """returns name of recently modified test"""
        max_mtime = 0
        most_recent_test = None
        for test in self.tests:
            mtime = os.stat(os.path.abspath(test)).st_mtime
            if mtime > max_mtime:
                max_mtime = mtime
                most_recent_test = test
        return most_recent_test

    def error_tests(self):
        """test error messages from tests in errs directory"""
        failures = []
        os.chdir("errs")
        tests = sorted(os.path.basename(t) for t in glob.glob("[0-9][0-9].py"))
        for test in tests:
            print("*** test:", test)
            try:
                checks = []
                with open(test, encoding='utf8') as fopen:
                    for line in fopen:
                        if line.startswith("#*"):
                            checks.append(line[1:].strip())
                cmd = f"{sys.executable} -m shedskin {test}".split()
                output = subprocess.run(
                    cmd, encoding="utf-8", capture_output=True, text=True
                ).stdout
                assert not [line for line in output if "Traceback" in line]
                for check in checks:
                    print(check)
                    assert [
                        line for line in output.splitlines() if line.startswith(check)
                    ]
                print(f"*** {GREEN}SUCCESS{RESET}:", test)
            except AssertionError:
                print(f"*** {RED}FAILURE{RESET}:", test)
                failures.append(test)
        os.chdir("..")
        return failures

    def rm_build(self):
        """remove build directory"""
        shutil.rmtree(self.build_dir)

    def mkdir_build(self):
        """create build directory"""
        os.makedirs(self.build_dir, exist_ok=True)

    def cmake_config(self, options: list[str], generator: Optional[str] = None):
        """cmake configuration phase"""
        opts = " ".join(options)
        cfg_cmd = f"cmake {opts} -S {self.source_dir} -B {self.build_dir}"
        if generator:
            cfg_cmd += ' -G "{generator}"'
        self.log.info(cfg_cmd)
        assert os.system(cfg_cmd) == 0

    def cmake_build(self, options: list[str]):
        """activate cmake build"""
        opts = " ".join(options)
        bld_cmd = f"cmake --build {self.build_dir} {opts}"
        self.log.info(bld_cmd)
        print("bld_cmd:", bld_cmd)
        assert os.system(bld_cmd) == 0

    def cmake_test(self, options: list[str]):
        """activate ctest"""
        opts = " ".join(options)
        if platform.system() == 'Windows':
            cfg = f"-C {self.options.build_type}"
        else:
            cfg = ""

        tst_cmd = f"ctest {cfg} --output-on-failure {opts} --test-dir {self.build_dir}"
        self.log.info(tst_cmd)
        assert os.system(tst_cmd) == 0

    def run_tests(self):
        """run tests as a test runner"""
        self.process(run_tests=True)

    def build(self):
        """build as a builder"""
        self.process(run_tests=False)

    def process(self, run_tests: bool = False):
        """process shedskin program with cmake"""
        start_time = time.time()

        cfg_options = [] if not getattr(self.options, 'cfg', None) else [f'-D{opt}' for opt in self.options.cfg]
        bld_options = []
        tst_options = []

        # -------------------------------------------------------------------------
        # cfg and bld options

        cfg_options.append("-DBUILD_EXECUTABLE=ON")
        if self.options.extmod:
            cfg_options.append("-DBUILD_EXTENSION=ON")

        if self.options.debug:
            cfg_options.append("-DDEBUG=ON")

        if self.options.generator:
            cfg_options.append(f"-G{self.options.generator}")

        if self.options.build_type:
            cfg_options.append(f" -DCMAKE_BUILD_TYPE={self.options.build_type}")

        if self.options.jobs:
            bld_options.append(f"--parallel {self.options.jobs}")
            tst_options.append(f"--parallel {self.options.jobs}")

        if self.options.ccache:
            if shutil.which("ccache"):
                cfg_options.append("-DCMAKE_CXX_COMPILER_LAUNCHER=ccache")
            else:
                self.log.warning("'ccache' not found")

        if self.options.conan:
            cfg_options.append("-DENABLE_CONAN=ON")

        elif self.options.spm:
            cfg_options.append("-DENABLE_SPM=ON")

        elif self.options.extproject:
            cfg_options.append("-DENABLE_EXTERNAL_PROJECT=ON")

        if not self.options.nowarnings:
            cfg_options.append("-DENABLE_WARNINGS=ON")

        if not cfg_options:
            self.log.warning("no configuration options selected")
            return

        if self.build_dir.exists() and self.options.reset:
            self.rm_build()

        if not self.build_dir.exists():
            self.mkdir_build()

        if self.options.conan:
            dpm = ConanDependencyManager(self.source_dir)
            dpm.generate_conanfile()
            dpm.install()

        elif self.options.spm:
            spm = ShedskinDependencyManager(self.source_dir)
            spm.install_all()

        if self.options.target:
            target_suffix = "-exe"
            for target in self.options.target:
                bld_options.append(f"--target {target}{target_suffix}")
                tst_options.append(f"--tests-regex {target}{target_suffix}")

        # -------------------------------------------------------------------------
        # test options

        if run_tests:
            if self.options.include:
                tst_options.append(f"--tests-regex {self.options.include}")

            if self.options.check:
                self.check(self.options.name)  # check python syntax

            if self.options.modified:
                most_recent_test = pathlib.Path(self.get_most_recent_test()).stem
                bld_options.append(f"--target {most_recent_test}")
                tst_options.append(f"--tests-regex {most_recent_test}")

            # nocleanup

            if self.options.pytest:
                try:
                    import pytest # noqa: F401

                    os.system("pytest")
                except ImportError:
                    self.log.exception("pytest not found")

            if self.options.run:
                target_suffix = "-exe"
                if self.options.extmod:
                    target_suffix = "-ext"
                bld_options.append(f"--target {self.options.run}{target_suffix}")
                tst_options.append(f"--tests-regex {self.options.run}")

            if self.options.stoponfail:
                tst_options.append("--stop-on-failure")

            if self.options.progress:
                tst_options.append("--progress")

        self.cmake_config(cfg_options)

        # print("cfg_options:", cfg_options)
        # print("bld_options:", bld_options)
        self.cmake_build(bld_options)

        if run_tests:
            self.cmake_test(tst_options)

        end_time = time.time()
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))
        print(f"Total time: {elapsed_time}\n")

    def run_error_tests(self):
        """run error tests"""
        start_time = time.time()

        if self.options.run_errs:
            failures = self.error_tests()
            if not failures:
                print(f"==> {GREEN}NO FAILURES, yay!{RESET}")
            else:
                print(f"==> {RED}TESTS FAILED:{RESET}", len(failures))
                print(failures)
        else:
            raise ValueError("option.run_errs not set")
            sys.exit()

        end_time = time.time()
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))
        print(f"Total time: {elapsed_time}\n")


class TestRunner(CMakeBuilder):
    """basic test runner"""

    def __init__(self, options: argparse.Namespace):
        self.options = options
        self.source_dir = pathlib.Path.cwd()
        self.build_dir = pathlib.Path("build")
        self.tests = sorted(glob.glob("./test_*/test_*.py", recursive=True))
        self.log = logging.getLogger(self.__class__.__name__)
