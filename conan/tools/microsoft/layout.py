import os

from conan.tools.microsoft.msbuild import msbuild_arch
from conan.errors import ConanException


def vs_layout(conanfile):
    """
    Initialize a layout for a typical Visual Studio project.

    :param conanfile: ``< ConanFile object >`` The current recipe object. Always use ``self``.
    """
    subproject = conanfile.folders.subproject
    conanfile.folders.source = subproject or "."
    conanfile.folders.generators = os.path.join(subproject, "conan") if subproject else "conan"
    conanfile.folders.build = subproject or "."
    conanfile.cpp.source.includedirs = ["include"]

    try:
        build_type = str(conanfile.settings.build_type)
    except ConanException:
        raise ConanException("The 'vs_layout' requires the 'build_type' setting")
    try:
        arch = str(conanfile.settings.arch)
    except ConanException:
        raise ConanException("The 'vs_layout' requires the 'arch' setting")

    if arch in {"None", "x86"}:
        bindirs = build_type

    elif arch := msbuild_arch(arch):
        bindirs = os.path.join(arch, build_type)
    else:
        raise ConanException(f"The 'vs_layout' doesn't work with the arch '{arch}'")
    conanfile.cpp.build.libdirs = [bindirs]
    conanfile.cpp.build.bindirs = [bindirs]
