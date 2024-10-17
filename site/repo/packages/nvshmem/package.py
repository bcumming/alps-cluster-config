# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Nvshmem(CMakePackage, CudaPackage):
    """NVSHMEM is a parallel programming interface based on OpenSHMEM that
    provides efficient and scalable communication for NVIDIA GPU
    clusters. NVSHMEM creates a global address space for data that spans
    the memory of multiple GPUs and can be accessed with fine-grained
    GPU-initiated operations, CPU-initiated operations, and operations on
    CUDA streams."""

    homepage = "https://developer.nvidia.com/nvshmem"

    maintainers("bvanessen")

    license("BSD-3-Clause-Open-MPI")

    version("3.0.6-4", sha256="4f435fdee320a365dd19d24b9f74df69b69886d3902ec99b16b553d485b18871")

    #depends_on("c", type="build")  # generated
    #depends_on("cxx", type="build")  # generated

    variant("cuda", default=True, description="Build with CUDA")
    variant("ucx", default=False, description="Build with UCX support")
    variant("ofi", default=True, description="Build with libfabric support")
    variant("nccl", default=True, description="Build with NCCL support")
    variant("gdrcopy", default=False, description="Build with gdrcopy support")
    variant("mpi", default=True, description="Build with MPI support")
    variant("shmem", default=False, description="Build with shmem support")
    variant(
        "gpu_initiated_support",
        default=False,
        description="Build with support for GPU initiated communication",
    )
    conflicts("~cuda")

    def url_for_version(self, version):
        ver_str = "{0}".format(version)
        directory = ver_str.split("-")[0]
        url_fmt = "https://developer.download.nvidia.com/compute/redist/nvshmem/{0}/source/nvshmem_src_{1}.txz"
        return url_fmt.format(directory, version)

    depends_on("mpi", when="+mpi")
    depends_on("libfabric", when="+ofi")
    depends_on("ucx", when="+ucx")
    depends_on("gdrcopy", when="+gdrcopy")
    depends_on("nccl", when="+nccl")

    def setup_build_environment(self, env):
        env.set("CUDA_HOME", self.spec["cuda"].prefix)
        env.set("NVSHMEM_PREFIX", self.prefix)

        if "+ofi" in self.spec:
            env.set("NVSHMEM_LIBFABRIC_SUPPORT", "1")
            env.set("LIBFABRIC_HOME", self.spec["libfabric"].prefix)

        if "+ucx" in self.spec:
            env.set("NVSHMEM_UCX_SUPPORT", "1")
            env.set("UCX_HOME", self.spec["ucx"].prefix)

        if "+gdrcopy" in self.spec:
            env.set("NVSHMEM_USE_GDRCOPY", "1")
            env.set("GDRCOPY_HOME", self.spec["gdrcopy"].prefix)

        if "+nccl" in self.spec:
            env.set("NVSHMEM_USE_NCCL", "1")
            env.set("NCCL_HOME", self.spec["nccl"].prefix)

        if "+mpi" in self.spec:
            env.set("NVSHMEM_MPI_SUPPORT", "1")
            env.set("MPI_HOME", self.spec["mpi"].prefix)

            if self.spec.satisfies("^spectrum-mpi") or self.spec.satisfies("^openmpi"):
                env.set("NVSHMEM_MPI_IS_OMPI", "1")
            else:
                env.set("NVSHMEM_MPI_IS_OMPI", "0")

        if "+shmem" in self.spec:
            env.set("NVSHMEM_SHMEM_SUPPORT", "1")
            env.set("SHMEM_HOME", self.spec["mpi"].prefix)

        if "+gpu_initiated_support" in self.spec:
            env.set("NVSHMEM_GPUINITIATED_SUPPORT", "1")

    def cmake_args(self):
        args = [
            self.define_from_variant("NVSHMEM_MPI_SUPPORT", "mpi"),
            self.define_from_variant("NVSHMEM_LIBFABRIC_SUPPORT", "ofi"),
            self.define_from_variant("NVSHMEM_UCX_SUPPORT", "ucx"),
            self.define_from_variant("NVSHMEM_USE_NCCL", "nccl"),
            self.define_from_variant("NVSHMEM_USE_GDRCOPY", "gdrcopy"),
        ]
        args.append("-DNVSHMEM_NVTX=ON")
        # disable all IB features
        args.append("-DNVSHMEM_IBGDA_SUPPORT=OFF")
        args.append("-DNVSHMEM_IBDEVX_SUPPORT=OFF")
        args.append("-DNVSHMEM_IBRC_SUPPORT=OFF")

        return args

    def setup_run_environment(self, env):
        # set environment variables tuned for slingshot / Alps
        env.set("NVSHMEM_REMOTE_TRANSPORT", "libfabric")
        env.set("NVSHMEM_LIBFABRIC_PROVIDER", "cxi")
        env.set("NVSHMEM_DISABLE_CUDA_VMM", "1")
