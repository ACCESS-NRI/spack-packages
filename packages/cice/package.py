# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install cice
#
# You can edit this file again by typing:
#
#     spack edit cice
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class Cice(CMakePackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "https://github.com/CICE-Consortium/CICE"
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

    variant("openmp", default=False, description="Enable OpenMP")
    
    
    cesmcoupled = variant(
        "cesmcoupled", 
        default=False,
        values=(
            True, False, 
            conditional(True, when="+access3")
        ),
        description="Set CESMCOUPLED CPP Flag"
    )

    # depends

    # set_variant
    variant("access3", default=False, description="Link to Access3 share")
    
    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")
    
    depends_on("parallelio@2.5.10: build_type==RelWithDebInfo")
    depends_on("parallelio fflags='-qno-opt-dynamic-align -convert big_endian -assume byterecl -ftz -traceback -assume realloc_lhs -fp-model source' cflags='-qno-opt-dynamic-align -fp-model precise -std=gnu99'", when="%intel")

    depends_on("access3-share+install_libraries", when="+access3")
    depends_on("access3-share+openmp+install_libraries", when="+access3+openmp")

    root_cmakelists_dir = "cmake"
    
    def cmake_args(self):
        args = [
            self.define("OM3_CICE_IO", "PIO"),
            self.define_from_variant("OM3_LIB_INSTALL", "install_libraries"),
            self.define_from_variant("OM3_OPENMP", "openmp"),
            self.define_from_variant("CESMCOUPLED", "cesmcoupled")
        ]

        # we need this for cmake to find MPI_Fortran
        args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))
        
        return args