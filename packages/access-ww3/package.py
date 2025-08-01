# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class AccessWw3(CMakePackage):
    """WAVEWATCH III® is a community wave modeling framework that includes the
    latest scientific advancements in the field of wind-wave modeling and
    dynamics. This package builds using the Access3Share common libraries for
    ACCESS3 models."""

    homepage = "https://github.com/noaa-emc/ww3/"
    git = "https://github.com/ACCESS-NRI/WW3"
    maintainers("anton-seaice", "harshula")
    license("LGPL-3.0-only", checked_by="anton-seaice")

    version("head", preferred=True)  # the default branch from git
    version("2025.03.0", commit="d980dec")

    variant("openmp", default=False, description="Enable OpenMP")
    variant(
        "access3",
        default=True,
        description="Install WW3 as library for Access3 models"
    )

    depends_on("access3-share", when="+access3")
    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")

    flag_handler = build_system_flags

    def cmake_args(self):
        args = [
            self.define_from_variant("WW3_OPENMP", "openmp"),
            self.define_from_variant("WW3_ACCESS3", "access3"),
        ]

        return args
