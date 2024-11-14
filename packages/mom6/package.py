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
#     spack install mom6
#
# You can edit this file again by typing:
#
#     spack edit mom6
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import CMakePackage, variant, version, depends_on


class Mom6(CMakePackage):
    """The Modular Ocean Model (MOM) version 6. """

    homepage = "https://github.com/ACCESS-NRI"
    git = "https://github.com/ACCESS-NRI/MOM6.git"
    submodules = True

    maintainers = ["minghangli-uni", "harshula"]
    
    # FIXME: Add the SPDX identifier of the project's license below.
    # See https://spdx.org/licenses/ for a list. Upon manually verifying
    # the license, set checked_by to your Github username.
    license("UNKNOWN", checked_by="github_user1")

    root_cmakelists_dir = "cmake"

    variant("openmp", default=False, description="Enable OpenMP")
    variant("mom_symmetric", default=False, description="Use symmetric memory in MOM6")

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")
    depends_on("esmf@8.3.0:")
    depends_on("esmf cflags='-fp-model precise' fflags='-fp-model precise'", when="%intel")
    depends_on("fortranxml@4.1.2:")
    depends_on("fms@2021.03: build_type==RelWithDebInfo precision=64 +large_file ~gfs_phys ~quad_precision")
    depends_on("fms +openmp", when="+openmp")
    depends_on("fms ~openmp", when="~openmp")

    def cmake_args(self):
        args = [
            self.define_from_variant("OM3_MOM_SYMMETRIC", "mom_symmetric"),
            self.define_from_variant("OM3_LIB_INSTALL", "install_libraries"),
            self.define_from_variant("OM3_OPENMP", "openmp"),
        ]
        args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))

        return args