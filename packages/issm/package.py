# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 Angus Gibson
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Issm(AutotoolsPackage):
    """Ice-sheet and Sea-Level System Model"""

    homepage = "https://issm.jpl.nasa.gov/"
    svn = "https://issm.ess.uci.edu/svn/issm/issm/trunk"

    version("develop")

    depends_on("autoconf", type="build")
    depends_on("automake", type="build")
    depends_on("libtool", type="build")
    depends_on("m4", type="build")

    depends_on("mpi")
    depends_on("petsc+metis+mumps+scalapack")
    depends_on("m1qn3")

    def autoreconf(self, spec, prefix):
        autoreconf("--install", "--verbose", "--force")

    def configure_args(self):
        args = [
          "--with-wrappers=no",
          "--enable-debugging",
          "--enable-development",
          "--enable-shared",
          "--without-kriging",
        ]
        args.append("--with-petsc-dir={0}".format(self.spec["petsc"].prefix))
        args.append("--with-metis-dir={0}".format(self.spec["metis"].prefix))
        args.append("--with-mumps-dir={0}".format(self.spec["mumps"].prefix))
        args.append("--with-m1qn3-dir={0}".format(self.spec["m1qn3"].prefix.lib))

        # Even though we set the MPI compilers manually, the build system
        # wants us to explicitly request an MPI-enabled build by telling
        # it the MPI include directory.
        args.append("--with-mpi-include={0}".format(self.spec["mpi"].prefix.include))
        args.append("CC=" + self.spec["mpi"].mpicc)
        args.append("CXX=" + self.spec["mpi"].mpicxx)
        args.append("FC=" + self.spec["mpi"].mpifc)
        args.append("F77=" + self.spec["mpi"].mpif77)

        return args
