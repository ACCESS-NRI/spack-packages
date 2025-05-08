# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
from spack.version.version_types import GitVersion, StandardVersion

class Mom5(CMakePackage):
    """MOM is a numerical ocean model based on the hydrostatic primitive equations."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/mom5.git"

    maintainers("dougiesquire", "harshula")

    # https://github.com/ACCESS-NRI/MOM5#LGPL-3.0-1-ov-file
    license("LGPL-3.0-only", checked_by="dougiesquire")

    version("mom_solo", branch="master", preferred=True)
    version("mom_sis", branch="master")
    version("access-om2", branch="master")
    version("legacy-access-om2-bgc", branch="master")
    version("access-esm1.6", branch="master")

    variant("build_type", default="RelWithDebInfo",
        description="CMake build type",
        values=("Debug", "Release", "RelWithDebInfo")
    )
    variant("deterministic", default=False, description="Deterministic build")

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-c@4.7.4:")
    depends_on("netcdf-fortran@4.5.2:")

    with when("@access-om2,access-esm1.6,legacy-access-om2-bgc"):
        depends_on("datetime-fortran")
        depends_on("libaccessom2+deterministic", when="+deterministic")
        depends_on("libaccessom2~deterministic", when="~deterministic")
        depends_on("oasis3-mct+deterministic", when="+deterministic")
        depends_on("oasis3-mct~deterministic", when="~deterministic")
        depends_on("access-fms")
        depends_on("access-generic-tracers")

    root_cmakelists_dir = "cmake/"

    phases = ["setup", "cmake", "build", "install"]

    # NOTE: The keys in the __types variable are required to check whether
    #       a valid version was passed in by the user.
    __types = {
        "mom_solo": "MOM5_SOLO",
        "mom_sis": "MOM5_SIS",
        "access-om2": "MOM5_ACCESS_OM",
        "access-esm1.6": "MOM5_ACCESS_ESM",
        "legacy-access-om2-bgc": "MOM5_ACCESS_OM_BGC"
    }
    __version = "INVALID"

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/mom5/tarball/{0}".format(version)
    
    def setup(self, spec, prefix):

        if isinstance(self.version, GitVersion):
            self.__version = self.version.ref_version.string
        elif isinstance(self.version, StandardVersion):
            self.__version = self.version.string
        else:
            print("ERROR: version=" + self.version.string)
            raise ValueError

        # The rest of the checks are only required if a __types member
        # variable exists
        if self.__version not in self.__types.keys():
            print("ERROR: The version must be selected from: " +
                    ", ".join(self.__types.keys()))
            raise ValueError

        print("INFO: version=" + self.__version +
            " type=" + self.__types[self.__version]
        )

    def cmake_args(self):
        args = [
            self.define("MOM5_TYPE", self.__types[self.__version]),
            self.define_from_variant("MOM5_DETERMINISTIC", "deterministic"),
        ]
        return args