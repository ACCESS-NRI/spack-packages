# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# Based on spack/var/spack/repos/builtin/packages/fiat/package.py

from spack.package import *


class AccessTestModelComponent(CMakePackage):
    """ACCESS Test Model Component is a small test FORTRAN model component
       used to test CI workflows."""

    homepage = "https://github.com/ACCESS-NRI/access-test-model"
    git = "https://github.com/ACCESS-NRI/access-test-model.git"

    maintainers("aidanheerdegen", "codegat", "harshula")

    license("Apache-2.0")

    version("main", branch="main", no_cache=True)

    variant("mpi", default=True, description="Use MPI")

    depends_on("mpi", when="+mpi")

    root_cmakelists_dir = "stub"

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/access-test-model/tarball/{0}".format(version)
