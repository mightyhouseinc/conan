from conan.api.output import ConanOutput
from conan.internal.api.detect_api import detect_os, detect_arch, default_msvc_runtime, \
    detect_libcxx, detect_cppstd, detect_compiler, default_compiler_version


def detect_defaults_settings():
    """ try to deduce current machine values without any constraints at all
    :return: A list with default settings
    """
    the_os = detect_os()
    result = [("os", the_os)]
    if arch := detect_arch():
        result.append(("arch", arch))
    compiler, version = detect_compiler()
    if not compiler:
        result.append(("build_type", "Release"))
        ConanOutput().warning("No compiler was detected (one may not be needed)")
        return result

    result.extend(
        (
            ("compiler", compiler),
            ("compiler.version", default_compiler_version(compiler, version)),
        )
    )
    runtime, runtime_version = default_msvc_runtime(compiler)
    if runtime:
        result.append(("compiler.runtime", runtime))
    if runtime_version:
        result.append(("compiler.runtime_version", runtime_version))
    if libcxx := detect_libcxx(compiler, version):
        result.append(("compiler.libcxx", libcxx))
    if cppstd := detect_cppstd(compiler, version):
        result.append(("compiler.cppstd", cppstd))
    result.append(("build_type", "Release"))
    return result
