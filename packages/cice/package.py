# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
# ----------------------------------------------------------------------------

from spack.package import *


class Cice(CMakePackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "https://github.com/CICE-Consortium/CICE"
    url = "https://github.com/CICE-Consortium/CICE/archive/refs/tags/CICE6.6.0.tar.gz"
    git = "https://github.com/ACCESS-NRI/CICE"
    submodules = True
    maintainers = ["anton-seaice", "harshula"]

    # FIXME: Add the SPDX identifier of the project's license below.
    # See https://spdx.org/licenses/ for a list. Upon manually verifying
    # the license, set checked_by to your Github username.
    license("UNKNOWN", checked_by="github_user1")

    variant(
        "driver", 
        default = "standalone" ,
        values = (
            "standalone",
            "nuopc/cmeps"
        )
    )

    variant("io_type", 
        default = "NetCDF" ,
        values = ("NetCDF", "PIO", "Binary"),
        description = "CICE IO Method"
    )

    variant("openmp", default=False, description="Enable OpenMP")
    variant("cesmcoupled", default=False, description="Set CESMCOUPLED CPP Flag")

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")

    depends_on("netcdf-fortran@4.6.0:", when="io_type=NetCDF")
    depends_on("parallelio@2.5.10: build_type==RelWithDebInfo", when="io_type=PIO")
    depends_on("parallelio fflags='-qno-opt-dynamic-align -convert big_endian -assume byterecl -ftz -traceback -assume realloc_lhs -fp-model source' cflags='-qno-opt-dynamic-align -fp-model precise -std=gnu99'", when="%intel io_type=PIO")

    depends_on("access3-share+install_libraries", when="driver=nuopc/cmeps")
    depends_on("access3-share+openmp+install_libraries", when="+openmp driver=nuopc/cmeps")

    root_cmakelists_dir = "cmake"
    
    def cmake_args(self):
        args = [
            self.define_from_variant("CICE_IO", "io_type"),
            self.define_from_variant("OPENMP", "openmp"),
            self.define_from_variant("CESMCOUPLED", "cesmcoupled")
        ]

        if self.spec.satisfies("driver=nuopc/cmeps"):
            args.append(self.define("ACCESS3_LIB_INSTALL", True))

        # we need this for cmake to find MPI_Fortran
        args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))
        
        return args