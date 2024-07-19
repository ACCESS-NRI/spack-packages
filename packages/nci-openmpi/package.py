# Adapted from https://github.com/spack/spack/blob/v0.20.0/var/spack/repos/builtin/packages/openmpi/package.py
# Scott Wales 2023
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class NciOpenmpi(Package):
    """
    Represents NCI's install of openmpi, where GCC and Intel variants of the
    library are stored under lib/GNU and lib/Intel respectively

    Not an installable package, this should instead be added to packages.yaml as::

        nci-openmpi:
          externals:
            - spec: nci-openmpi@4.1.4
              prefix: /apps/openmpi/4.1.4
              modules:
              - openmpi/4.1.4
          buildable: False
    """

    # This is a mpi provider
    provides("mpi@3")

    def setup_run_environment(self, env):
        # The same as the normal openmpi package
        env.set("MPICC", join_path(self.prefix.bin, "mpicc"))
        env.set("MPICXX", join_path(self.prefix.bin, "mpic++"))
        env.set("MPIF77", join_path(self.prefix.bin, "mpif77"))
        env.set("MPIF90", join_path(self.prefix.bin, "mpif90"))

        # Add the compiler-specific fortran paths
        if self.spec.satisfies("%intel"):
            finc_path = join_path(self.prefix.include, "Intel")
            flib_path = join_path(self.prefix.lib, "Intel")
        elif self.spec.satisfies("%gcc"):
            finc_path = join_path(self.prefix.include, "GNU")
            flib_path = join_path(self.prefix.lib, "GNU")

        env.append_flags("OMPI_FCFLAGS", "-I" + finc_path)
        env.append_flags("OMPI_LDFLAGS", "-L" + self.prefix.lib)
        env.append_flags("OMPI_LDFLAGS", "-L" + flib_path)

    # The following is reproduced from the builtin openmpi spack package
    def setup_dependent_build_environment(self, env, dependent_spec):

        # Use the spack compiler wrappers under MPI
        env.set("OMPI_CC", spack_cc)
        env.set("OMPI_CXX", spack_cxx)
        env.set("OMPI_FC", spack_fc)
        env.set("OMPI_F77", spack_f77)

    def setup_dependent_package(self, module, dependent_spec):
        self.spec.mpicc = join_path(self.prefix.bin, "mpicc")
        self.spec.mpicxx = join_path(self.prefix.bin, "mpic++")
        self.spec.mpifc = join_path(self.prefix.bin, "mpif90")
        self.spec.mpif77 = join_path(self.prefix.bin, "mpif77")

        self.spec.mpicxx_shared_libs = [
            join_path(self.prefix.lib, "libmpi_cxx.{0}".format(dso_suffix)),
            join_path(self.prefix.lib, "libmpi.{0}".format(dso_suffix)),
        ]
