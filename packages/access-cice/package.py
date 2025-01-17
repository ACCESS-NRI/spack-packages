# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0
# ----------------------------------------------------------------------------

from spack.package import *


class AccessCice(CMakePackage):
    """CICE is a computationally efficient model for simulating the growth, melting, 
    and movement of polar sea ice. CICE is maintained and developed by the CICE-Consortium. 
    This package builds using the Access3Share common libraries for ACCESS 3 models."""

    homepage = "https://github.com/CICE-Consortium/CICE"
    url = "https://github.com/CICE-Consortium/CICE/archive/refs/tags/CICE6.6.0.tar.gz"
    version("6.6.0", md5="1c678c0af67bf09f92c0a861344c3a92")
    git = "https://github.com/ACCESS-NRI/CICE"
    submodules = True
    maintainers = ["anton-seaice", "harshula"]

    # see license file in at https://github.com/CICE-Consortium/CICE
    license("LicenseRef-CICE", checked_by="anton-seaice")

    # variant("openmp", default=False, description="Enable OpenMP")
    variant("cesmcoupled", default=False, description="Set CESMCOUPLED CPP Flag")
    variant("access3", default=True, description="Install CICE as library for Access3 models") 

    variant("io_type", 
        default="NetCDF",
        values=("NetCDF", "PIO", "Binary"),
        description="CICE IO Method"
    )

    variant(
        "build_type",
        default="Release",
        description="The build type to build",
        values=("Debug", "Release"),
    )

    depends_on("access3-share", when="+access3") 
    # depends_on("access3-share+openmp", when="+openmp+access3")

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:", when="io_type=NetCDF")
    depends_on("parallelio@2.5.10: build_type==RelWithDebInfo", when="io_type=PIO")
    depends_on("parallelio fflags='-qno-opt-dynamic-align -convert big_endian -assume byterecl -ftz -traceback -assume realloc_lhs -fp-model source' cflags='-qno-opt-dynamic-align -fp-model precise -std=gnu99'", when="%intel io_type=PIO")

    root_cmakelists_dir = "cmake"
    
    def cmake_args(self):
        args = [
            self.define_from_variant("CICE_IO", "io_type"),
            # self.define_from_variant("OPENMP", "openmp"),
            self.define_from_variant("CESMCOUPLED", "cesmcoupled"),
            self.define_from_variant("ACCESS3_CICE", "access3")
        ]

        # we need this for cmake to find MPI_Fortran
        args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))
        
        return args