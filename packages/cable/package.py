# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2022 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

# See https://spack.readthedocs.io/en/latest/packaging_guide.html for a guide
# on how this file works.


class Cable(CMakePackage):
    """The CSIRO Atmosphere Biosphere Land Exchange (CABLE) model."""

    homepage = "https://github.com/CABLE-LSM/CABLE"
    git = "https://github.com/CABLE-LSM/CABLE.git"

    maintainers("SeanBryan51")

    version("main", branch="main")

    def url_for_version(self, version):
        return "https://github.com/CABLE-LSM/CABLE/tarball/{0}".format(version)

    variant(
        "mpi",
        default=True,
        description="Build MPI executable.",
    )
    variant(
        "build_type",
        default="Release",
        description="CMake build type",
        values=("Debug", "Release"),
    )

    depends_on("netcdf-fortran@4.5.2:")
    depends_on("mpi", when="+mpi")

    def cmake_args(self):
        args = []
        args.append(self.define_from_variant("CABLE_MPI", "mpi"))
        return args
