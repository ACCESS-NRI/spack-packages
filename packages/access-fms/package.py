# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import find_headers, find_libraries

# Based on upstream $spack/var/spack/repos/builtin/packages/fms/package.py
class AccessFms(CMakePackage):
    """GFDL's Flexible Modeling System (FMS) is a software environment
    that supports the efficient development, construction, execution,
    and scientific interpretation of atmospheric, oceanic, and climate
    system models. This is ACCESS-NRI's fork."""

    homepage = "https://github.com/ACCESS-NRI/FMS"
    git = "https://github.com/ACCESS-NRI/FMS.git"

    license("LGPL-3.0-or-later")

    maintainers("harshula")

    version("master", branch="master")
    # TODO: Needs to be changed once changes to build system enter master.
    version("development", branch="development", preferred=True)

    variant("gfs_phys", default=True, description="Use GFS Physics")
    variant("large_file", default=False, description="Enable compiler definition -Duse_LARGEFILE.")
    variant(
        "internal_file_nml",
        default=True,
        description="Enable compiler definition -DINTERNAL_FILE_NML.",
    )

    depends_on("netcdf-c")
    depends_on("netcdf-fortran")
    depends_on("mpi")

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/FMS/tarball/{0}".format(version)

    @property
    def headers(self):
        return find_headers(
            "*", root=self.prefix, recursive=True
        )

    @property
    def libs(self):
        libraries = ["libfms_r4", "libfms_r8"]
        return find_libraries(
            libraries, root=self.prefix, shared=False, recursive=True
        )

    def cmake_args(self):
        args = [
            self.define_from_variant("GFS_PHYS"),
            self.define_from_variant("LARGEFILE", "large_file"),
            self.define_from_variant("INTERNAL_FILE_NML"),
        ]

        return args
