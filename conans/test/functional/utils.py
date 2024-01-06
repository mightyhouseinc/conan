from conan.tools.microsoft.visual import vcvars_command


def check_vs_runtime(artifact, client, vs_version, build_type, architecture="amd64",
                     static_runtime=False, subsystem=None):
    vcvars = vcvars_command(version=vs_version, architecture=architecture)
    normalized_path = artifact.replace("/", "\\")
    if static := artifact.endswith(".a") or artifact.endswith(".lib"):
        client.run_command(f'{vcvars} && DUMPBIN /NOLOGO /DIRECTIVES "{artifact}"')
        if build_type == "Debug":
            assert "RuntimeLibrary=MDd_DynamicDebug" in client.out
        else:
            assert "RuntimeLibrary=MD_DynamicRelease" in client.out

    else:
        cmd = f'{vcvars} && dumpbin /nologo /dependents "{normalized_path}"'
        client.run_command(cmd)
        assert "KERNEL32.dll" in client.out
        if subsystem:
            if subsystem in ("mingw32", "mingw64"):
                assert "msvcrt.dll" in client.out
                if static_runtime:
                    assert "libstdc++-6.dll" not in client.out
                else:
                    assert "libstdc++-6.dll" in client.out
                if subsystem == "mingw32":
                    if static_runtime:
                        assert "libgcc_s_dw2-1.dll" not in client.out
                    else:
                        assert "libgcc_s_dw2-1.dll" in client.out
            elif subsystem == "msys2":
                assert "msys-2.0.dll" in client.out
                if static_runtime:
                    assert "msys-stdc++-6.dll" not in client.out
                else:
                    assert "msys-stdc++-6.dll" in client.out
            elif subsystem == "cygwin":
                assert "cygwin1.dll" in client.out
                if static_runtime:
                    assert "cygstdc++-6.dll" not in client.out
                else:
                    assert "cygstdc++-6.dll" in client.out
            elif subsystem == "ucrt64":
                assert "api-ms-win-crt-" in client.out
                if static_runtime:
                    assert "libstdc++-6.dll" not in client.out
                else:
                    assert "libstdc++-6.dll" in client.out
            elif subsystem == "clang64":
                assert "api-ms-win-crt-" in client.out
                if static_runtime:
                    assert "libunwind.dll" not in client.out
                    assert "libc++.dll" not in client.out
                else:
                    assert "libunwind.dll" in client.out
                    assert "libc++.dll" in client.out
            else:
                raise Exception(f"unknown {subsystem}")
        elif static_runtime:
            assert "MSVC" not in client.out
            assert "VCRUNTIME" not in client.out
        else:
            if build_type == "Debug":
                assert "ucrtbased" in client.out
            else:
                assert "api-ms-win-crt-" in client.out
            if vs_version not in ["15", "16", "17"]:
                raise NotImplementedError()
            debug = "D" if build_type == "Debug" else ""
            assert f"MSVCP140{debug}.dll" in client.out
            assert f"VCRUNTIME140{debug}.dll" in client.out


def check_exe_run(output, names, compiler, version, build_type, arch, cppstd, definitions=None,
                  cxx11_abi=None, subsystem=None, extra_msg=""):
    output = str(output)
    names = names if isinstance(names, list) else [names]

    for name in names:
        if extra_msg:  # For ``conan new`` templates
            assert f"{name} {extra_msg} {build_type}" in output
        else:
            assert f"{name}: {build_type}" in output
        if compiler == "msvc":
            if arch == "armv8":
                assert f"{name} _M_ARM64 defined" in output
            elif arch == "x86":
                assert f"{name} _M_IX86 defined" in output
            elif arch == "x86_64":
                assert f"{name} _M_X64 defined" in output
            else:
                assert arch is None, "checked don't know how to validate this architecture"

            if version:
                assert f"{name} _MSC_VER{version}" in output
            if cppstd:
                assert f"{name} _MSVC_LANG20{cppstd}" in output

        elif compiler in ["gcc", "clang", "apple-clang"]:
            if compiler == "gcc":
                assert f"{name} __GNUC__" in output
                assert "clang" not in output
                if version:  # FIXME: At the moment, the GCC version is not controlled, will change
                    major, minor = version.split(".")[:2]
                    assert f"{name} __GNUC__{major}" in output
                    assert f"{name} __GNUC_MINOR__{minor}" in output
            elif compiler == "clang":
                assert f"{name} __clang_" in output
                if version:
                    major, minor = version.split(".")[:2]
                    assert f"{name} __clang_major__{major}" in output
                    assert f"{name} __clang_minor__{minor}" in output
            elif compiler == "apple-clang":
                assert f"{name} __apple_build_version__" in output
                if version:
                    major, minor = version.split(".")[:2]
                    assert f"{name} __apple_build_version__{major}{minor}" in output
            if arch == "armv8":
                assert f"{name} __aarch64__ defined" in output
            elif arch == "x86":
                assert f"{name} __i386__ defined" in output
            elif arch == "x86_64":
                assert f"{name} __x86_64__ defined" in output
            else:
                assert arch is None, "checked don't know how to validate this architecture"

            if cppstd:
                cppstd_value = {"98": "199711",
                                "11": "201103",
                                "14": "201402",
                                "17": "201703"}[cppstd]
                assert f"{name} __cplusplus{cppstd_value}" in output

            if cxx11_abi is not None:
                assert f"{name} _GLIBCXX_USE_CXX11_ABI {cxx11_abi}" in output

        if definitions:
            for k, v in definitions.items():
                assert f"{k}: {v}" in output

        if subsystem:
            if subsystem == "msys2":
                assert "__MSYS__" in output
                assert "__CYGWIN__" in output
                assert "MINGW" not in output
            elif subsystem in ("mingw32", "mingw64"):
                assert "__MINGW32__" in output
                assert "__CYGWIN__" not in output
                assert "__MSYS__" not in output
                if subsystem == "mingw64":
                    assert "__MINGW64__" in output
                else:
                    assert "MING64" not in output
            elif subsystem == "cygwin":
                assert "__CYGWIN__" in output
                assert "__MINGW32__" not in output
                assert "__MINGW64__" not in output
                assert "__MSYS__" not in output
            else:
                raise Exception(f"unknown subsystem {subsystem}")
        else:
            assert "CYGWIN" not in output
            assert "MINGW" not in output
            assert "MSYS" not in output
