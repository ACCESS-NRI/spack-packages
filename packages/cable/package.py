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
        "library",
        default=False,
        values=(
            conditional("ESM1.6", when="@access-esm1.6")
        ),
        description="Build CABLE science library object.",
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
        args.append(self.define("CABLE_LIBRARY", self.spec.variants["library"].value != "none"))
        args.append(self.define_from_variant("CABLE_LIBRARY_TARGET", "library"))
        return args
