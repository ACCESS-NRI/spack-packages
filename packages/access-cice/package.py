# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class AccessCice(CMakePackage):
    """CICE is a computationally efficient model for simulating the growth, melting, 
    and movement of polar sea ice. CICE is maintained and developed by the CICE-Consortium. 
    This package builds using the Access3Share common libraries for ACCESS 3 models."""

    homepage = "https://github.com/CICE-Consortium/CICE"
    git = "https://github.com/ACCESS-NRI/CICE"
    submodules = True
    maintainers("anton-seaice", "harshula")

    # see license file at https://github.com/CICE-Consortium/CICE
    license("LicenseRef-CICE", checked_by="anton-seaice")

    variant("openmp", default=False, description="Enable OpenMP")
    variant("access3", default=True, description="Install CICE as library for Access3 models") 
    variant("cesmcoupled", default=False, description="Set CESMCOUPLED CPP Flag")

    variant("io_type", 
        default="NetCDF",
        values=("NetCDF", "PIO", "Binary"),
        description="CICE IO Method"
    )

    depends_on("access3-share", when="+access3") 
    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:", when="io_type=NetCDF")
    depends_on("parallelio@2.5.10:", when="io_type=PIO")

    root_cmakelists_dir = "configuration/scripts/cmake"

    def cmake_args(self):
        args = [
            self.define_from_variant("OPENMP", "openmp"),
            self.define_from_variant("CICE_IO", "io_type"),
            self.define_from_variant("ACCESS3_CICE", "access3"),
            self.define_from_variant("CESMCOUPLED", "cesmcoupled"),
        ]

        return args
