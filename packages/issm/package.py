# Copyright 2013-2023 Lawrence Livermore National Security, 
# LLC and other Spack Project Developers. See the top-level COPYRIGHT 
# file for details.
#
# Copyright 2023 Angus Gibson
# Modified by Justin Kin Jun Hew, 2025
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Issm(AutotoolsPackage):
    """Ice-sheet and Sea-Level System Model"""

    homepage = "https://issm.jpl.nasa.gov/"
    git      = "https://github.com/ACCESS-NRI/ISSM.git"

    version("4.24", sha256="c71d870e63f0ce3ae938d6a669e80dc2cecef827084db31a4b2cfc3a26a44820")

    #
    # Variants
    #
    variant("wrappers", default=False,
            description="Enable building with MPI wrappers")

    # If you want to make external Fortran linking optional or specialized,
    # you can create a separate variant for it, but typically you might
    # rely on Spack's compiler wrappers for Fortran libraries.

    #
    # Build dependencies
    #
    depends_on("autoconf", type="build")
    depends_on("automake", type="build")
    depends_on("libtool",  type="build")
    depends_on("m4",       type="build")

    #
    # Required libraries
    #
    depends_on("mpi")
    depends_on("petsc+metis+mumps+scalapack")
    depends_on("m1qn3")

    #
    # Optional libraries
    #
    depends_on('access-triangle-git', when='+wrappers')
    depends_on("parmetis",  when="+wrappers")
    depends_on("python@3.9.0:3.9", when="+wrappers", type=("build", "run"))
    depends_on("py-numpy",         when="+wrappers", type=("build", "run"))

    def url_for_version(self, version):
        # Example of how you might form a URL for a particular version:
        return "https://github.com/ACCESS-NRI/ISSM/tarball/v{0}".format(version)

    def autoreconf(self, spec, prefix):
        # If the repo has an Autotools build system, run autoreconf:
        autoreconf("--install", "--verbose", "--force")

    def configure_args(self):
        """Populate configure arguments, including optional flags to mimic 
        your manual `./configure` invocation on Gadi."""
        args = [
            "--enable-debugging",
            "--enable-development",
            "--enable-shared",
            "--without-kriging",
        ]

        #
        # Wrappers
        #
        if "+wrappers" in self.spec:
            args.append("--with-wrappers=yes")
        else:
            args.append("--with-wrappers=no")

        #
        # MPI: Even if we use Spack's MPI wrappers, the build system may 
        # want explicit mention of MPI includes and compilers:
        #
        args.append("--with-mpi-include={0}".format(self.spec["mpi"].prefix.include))
        args.append("CC=" + self.spec["mpi"].mpicc)
        args.append("CXX=" + self.spec["mpi"].mpicxx)
        args.append("FC=" + self.spec["mpi"].mpifc)
        args.append("F77=" + self.spec["mpi"].mpif77)

        #
        # PETSc, MUMPS, METIS, SCALAPACK, etc.
        # (Spack typically puts these in the compiler/link environment,
        #  but if the ISSM configure script looks for explicit --with-* 
        #  flags, we pass them.)
        #
        args.append("--with-petsc-dir={0}".format(self.spec["petsc"].prefix))
        args.append("--with-metis-dir={0}".format(self.spec["metis"].prefix))
        args.append("--with-mumps-dir={0}".format(self.spec["mumps"].prefix))
        # If you rely on sca/lapack from PETSc, these lines might 
        # not be strictly necessary. If ISSM's configure script 
        # checks them individually, add them:
        args.append("--with-scalapack-dir={0}".format(self.spec["scalapack"].prefix))
        args.append("--with-parmetis-dir={0}".format(self.spec["parmetis"].prefix))
        args.append("--with-triangle-dir={0}".format(self.spec["triangle"].prefix))

        #
        # M1QN3
        #
        # Some codes want the actual library subdir for m1qn3, 
        # e.g. "prefix.lib" or "prefix" depending on the configure logic:
        #
        args.append("--with-m1qn3-dir={0}".format(self.spec["m1qn3"].prefix.lib))

        args.append("--with-python-version=3.9")

        args.append("--with-python-dir={0}".format(self.spec["python"].prefix))

        numpy_prefix = self.spec["py-numpy"].prefix
        # Possibly site-packages is in something like: 
        #   numpy_prefix.lib/python3.9/site-packages
        # or similar. You can either guess or do something more dynamic. 
        args.append("--with-python-numpy-dir={0}".format(numpy_prefix))


        return args
