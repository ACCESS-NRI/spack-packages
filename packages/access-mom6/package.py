# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class AccessMom6(CMakePackage):
    """The Modular Ocean Model (MOM) describes the numerical ocean models
    originating from NOAA/GFDL. They are used to simulate ocean currents at both
    regional and global scales, enabling scientists to answer fundamental
    questions about the role of the ocean in the dynamics of the global climate.
    This package builds using the Access3Share common libraries for ACCESS3
    models."""

    homepage = "https://github.com/ACCESS-NRI/MOM6"
    git = "https://github.com/ACCESS-NRI/MOM6.git"
    submodules = True
    maintainers("minghangli-uni", "harshula")

    # see license file in https://github.com/ACCESS-NRI/MOM6/blob/e92c971084e185cfd3902f18072320b45d583a54/LICENSE.md
    license("LGPL-3.0-only", checked_by="minghangli-uni")

    version("2025.02.001", commit="a5f4397")
    version("2025.02.000", commit="e088c8b")

    variant("openmp", default=False, description="Enable OpenMP")
    variant("asymmetric_mem", default=False, description="Use asymmetric memory in MOM6")
    variant(
        "access3",
        default=True,
        description="Install MOM6 as library for Access3 models"
    )

    depends_on("access3-share", when="+access3")
    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")
    depends_on("fms@2023.02: precision=64 +large_file ~gfs_phys ~quad_precision")
    depends_on("fms@2025.02: +openmp", when="+openmp")
    depends_on("fms ~openmp", when="~openmp")
    depends_on("access-generic-tracers ~use_access_fms", when="@2025.02.001:")

    flag_handler = build_system_flags

    def cmake_args(self):
        args = [
            self.define_from_variant("MOM6_OPENMP", "openmp"),
            self.define_from_variant("MOM6_ASYMMETRIC", "asymmetric_mem"),
            self.define_from_variant("MOM6_ACCESS3", "access3"),
        ]

        return args
