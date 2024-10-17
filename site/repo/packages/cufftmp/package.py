# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os
import platform

import spack.compilers
from spack.package import *

# PLAN
# provide both x86_64 and aarch64 in the same tar ball, in x86_64 and aarch64 sub-directories

class Cufftmp(Package):
    """the cuffwmp package - CSCS custom version for installation outside nvhpc-sdk """

    homepage = "https://docs.nvidia.com/hpc-sdk/cufftmp/index.html"
    url = "https://jfrog.svc.cscs.ch/artifactory/cray-mpich/cray-mpich-8.1.26.tar.gz"
    maintainers = ["bcumming"]

    version(
            "11.2.6",
            sha256="3b95fa899054c429153dd0dfe91b447c6c2b707159fdb65512570506dfce4a26",
            url="file:///capstor/scratch/cscs/bcumming/software/cufftmp-11.2.6.tar.gz"
    )

    # Fix up binaries with patchelf.
    depends_on("patchelf", type="build")
    depends_on("nccl")
    depends_on("nvshmem")
    depends_on("cuda")
    depends_on("cray-mpich")
    depends_on("libfabric@1:", type="link")

    def get_rpaths(self):
        # Those rpaths are already set in the build environment, so
        # let's just retrieve them.
        pkgs = os.getenv("SPACK_RPATH_DIRS", "").split(":")
        pkgs_store = os.getenv("SPACK_STORE_RPATH_DIRS", "").split(":")
        compilers = os.getenv("SPACK_COMPILER_IMPLICIT_RPATHS", "").split(":")
        return ":".join([p for p in pkgs + compilers + pkgs_store if p])

    def should_patch(self, file):
        # Returns true if non-symlink ELF file.
        if os.path.islink(file):
            return False
        try:
            with open(file, "rb") as f:
                return f.read(4) == b"\x7fELF"
        except OSError:
            return False

    def install(self, spec, prefix):
        install_tree("include", os.path.join(prefix, "include"))
        install_tree("lib", os.path.join(prefix, "lib"))

    @run_after("install")
    def fixup_binaries(self):
        patchelf = which("patchelf")
        rpath = self.get_rpaths()
        for root, _, files in os.walk(self.prefix):
            for name in files:
                f = os.path.join(root, name)
                if not self.should_patch(f):
                    continue
                patchelf("--force-rpath", "--set-rpath", rpath, f, fail_on_error=False)

    #@run_after("install")
    #def fixup_pkgconfig(self):
    #    for root, _, files in os.walk(self.prefix):
    #        for name in files:
    #            if name[-3:] == '.pc':
    #                f = os.path.join(root, name)
    #                filter_file("@@PREFIX@@", self.prefix, f, string=True)

