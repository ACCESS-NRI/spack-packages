# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2022 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class Libaccessom2(CMakePackage):
    """libaccessom2 is a library that is linked into all of the ACCESS-OM2 component models, including YATM, CICE and MOM. libaccessom2 provides functionality used by all models as well as providing a interface to inter-model communication and synchronisation tasks."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/libaccessom2.git"

    maintainers = ["harshula"]

    version("master", branch="master")

    variant("deterministic", default=False, description="Deterministic build.")
    variant("optimisation_report", default=False, description="Generate optimisation reports.")
    variant('build_type',
            default='Release',
            description='The build type to build',
            values=('Debug', 'Release')
    )

    depends_on("cmake@3.20:", type="build")
    depends_on("pkgconf", type="build")
    # Depend on virtual package "mpi".
    depends_on("mpi")
    depends_on("oasis3-mct+deterministic", when="+deterministic")
    depends_on("oasis3-mct~deterministic", when="~deterministic")
    depends_on("datetime-fortran")
    depends_on("json-fortran")
    depends_on("netcdf-fortran@4.5.2:")

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/libaccessom2/tarball/{0}".format(version)

    def cmake_args(self):
        return [self.define_from_variant('DETERMINISTIC', "deterministic"),
                self.define_from_variant('OPTIMISATION_REPORT', "optimisation_report")]
