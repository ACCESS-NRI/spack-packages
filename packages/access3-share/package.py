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
#     spack install access3-share
#
# You can edit this file again by typing:
#
#     spack edit access3-share
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class Access3Share(CMakePackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "https://www.example.com"
    git = "https://github.com/ACCESS-NRI/access3-share"
    submodules = True
    maintainers = ["anton-seaice", "harshula"]

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers("github_user1", "github_user2")

    # FIXME: Add the SPDX identifier of the project's license below.
    # See https://spdx.org/licenses/ for a list. Upon manually verifying
    # the license, set checked_by to your Github username.
    license("UNKNOWN", checked_by="github_user1")

    # FIXME: Add dependencies if required.
    # depends_on("foo")

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")
    depends_on("esmf@8.3.0:")
    depends_on("esmf cflags='-fp-model precise' fflags='-fp-model precise'", when="%intel")
    depends_on("fortranxml@4.1.2:")

    depends_on("parallelio@2.5.10: build_type==RelWithDebInfo")
    depends_on("parallelio fflags='-qno-opt-dynamic-align -convert big_endian -assume byterecl -ftz -traceback -assume realloc_lhs -fp-model source' cflags='-qno-opt-dynamic-align -fp-model precise -std=gnu99'", when="%intel")

    flag_handler = CMakePackage.build_system_flags

    def cmake_args(self):

        args = []

        args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))

        return args