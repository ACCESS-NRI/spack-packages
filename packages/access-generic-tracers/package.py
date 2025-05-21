# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import find_libraries

class AccessGenericTracers(CMakePackage):
    """This is a fork of the NOAA-GFDL/ocean_BGC repo managed by NOAA-GFDL.
    It contains a collection of tracers and associated code for use with
    the MOM and GOLD ocean models. This fork includes generic tracer
    implementations of the suite of WOMBAT models used in ACCESS earth-system
    models."""

    homepage = "https://github.com/ACCESS-NRI/GFDL-generic-tracers"
    git = "https://github.com/ACCESS-NRI/GFDL-generic-tracers.git"

    maintainers("harshula")

    version("master", branch="master")
    # TODO: Needs to be changed once changes to build system enter master.
    version("development", branch="development", preferred=True)

    # NOTE: access-fms@mom5 should be used in OM2, ESM1.5 and ESM1.6 to preserve
    # answers with previous releases
    variant(
        "use_access_fms",
        default=True,
        description="If True, depend on access-fms, otherwise depend on fms"
    )

    depends_on("access-mocsy")
    depends_on("access-fms", when="+use_access_fms")
    depends_on("fms@2025.02:", when="~use_access_fms")
    depends_on("mpi")

    flag_handler = build_system_flags

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/GFDL-generic-tracers/tarball/{0}".format(version)

    @property
    def libs(self):
        libraries = find_libraries(
            "libgtracers", root=self.prefix, shared=False, recursive=True
        )
        # mocsy is an internal lib dependency of this static library.
        # Hence we need to propagate it.
        return libraries + self.spec["access-mocsy"].libs
