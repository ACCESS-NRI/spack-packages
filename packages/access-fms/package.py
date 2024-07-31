# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class AccessFms(CMakePackage):
    """GFDL's Flexible Modeling System (FMS) is a software environment
    that supports the efficient development, construction, execution,
    and scientific interpretation of atmospheric, oceanic, and climate
    system models. This is ACCESS-NRI's fork."""

    homepage = "https://github.com/ACCESS-NRI/FMS"
    git = "https://github.com/ACCESS-NRI/FMS.git"

    license("LGPL-3.0-or-later")

    maintainers("harshula")

    version("master", branch="master", preferred=True)
    version("development", branch="development")

    variant("gfs_phys", default=True, description="Use GFS Physics")
    variant("openmp", default=True, description="Use OpenMP")
    variant("large_file", default=False, description="Enable compiler definition -Duse_LARGEFILE.")
    variant(
        "internal_file_nml",
        default=True,
        description="Enable compiler definition -DINTERNAL_FILE_NML.",
    )

    depends_on("netcdf-c")
    depends_on("netcdf-fortran")
    depends_on("mpi")

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/FMS/tarball/{0}".format(version)

    def cmake_args(self):
        args = [
            self.define_from_variant("GFS_PHYS"),
            self.define_from_variant("OPENMP"),
            self.define_from_variant("LARGEFILE", "large_file"),
            self.define_from_variant("INTERNAL_FILE_NML"),
        ]

        args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))

        return args
