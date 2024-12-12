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
#     spack install access3-exe
#
# You can edit this file again by typing:
#
#     spack edit access3-exe
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class Access3Exe(CMakePackage):
    """FIXME: Put a proper description of your package here."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://www.example.com"
    git = "https://github.com/ACCESS-NRI/access3-share"
    submodules = True


    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers("github_user1", "github_user2")

    # FIXME: Add the SPDX identifier of the project's license below.
    # See https://spdx.org/licenses/ for a list. Upon manually verifying
    # the license, set checked_by to your Github username.
    license("UNKNOWN", checked_by="github_user1")

    # version("3-share", sha256="fe86962fde9479ebb5f34528a81f650d69661d398d27a35d950e41d20a577bda")

    # FIXME: Add dependencies if required.
    # depends_on("foo")

    version("main", branch="main", submodules=True)

    variant(
        "build_type",
        default="Release",
        description="The build type to build",
        values=("Debug", "Release"),
    )
    variant(
        "configurations",
        default="MOM6-CICE6, CICE6-WW3, MOM6-CICE6-WW3",
        values=(
            "MOM6",
            "CICE6",
            "WW3",
            "MOM6-WW3",
            "MOM6-CICE6",
            "CICE6-WW3",
            "MOM6-CICE6-WW3",
        ),
        multi=True,
        description="ACCESS-OM3 configurations to build",
    )
    
    variant("openmp", default=False, description="Enable OpenMP")
    
    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("access-cice driver=nuopc/cmeps io_type=PIO +cesmcoupled")
    
    flag_handler = CMakePackage.build_system_flags

    def cmake_args(self):

        args = [
            self.define_from_variant("OPENMP", "openmp"),
            self.define("CESMCOUPLED", True)
        ]

        # we need this for cmake to find MPI_Fortran
        args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))
        
        return args
