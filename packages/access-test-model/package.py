# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# Based on spack/var/spack/repos/builtin/packages/fiat/package.py

from spack.package import *


class AccessTestModel(CMakePackage):
    """ACCESS Test Model is a small test FORTRAN model component
       used to test CI workflows."""

    homepage = "https://github.com/ACCESS-NRI/ACCESS-TEST-model"
    git = "https://github.com/ACCESS-NRI/ACCESS-TEST-model.git"

    maintainers("aidanheerdegen", "codegat", "harshula")

    license("Apache-2.0")

    version("main", branch="main", no_cache=True)

    variant("mpi", default=True, description="Use MPI")

    depends_on("mpi", when="+mpi")

    root_cmakelists_dir = "stub"

    def cmake_args(self):
        args = [
            self.define_from_variant("ENABLE_MPI", "mpi"),
        ]
        return args
