# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

# supported model configurations
KNOWN_CONF = (
    "MOM6",
    "CICE6",
    "WW3",
    "MOM6-WW3",
    "MOM6-CICE6",
    "CICE6-WW3",
    "MOM6-CICE6-WW3",
)

class Access3(CMakePackage):
    """Executable build for ACCESS version 3 climate models. The exectuable is
    defined in Community Mediator for Earth Prediction Systems (CMEPS).
    Currently implemented for ACCESS-OM3, and in the future may support
    ACCESS-CM3 and ACCESS-ESM3. This is a companion package to Access3Share
    which builds the shared libraries."""

    homepage = "https://github.com/ACCESS-NRI/access3-share"
    git = "https://github.com/ACCESS-NRI/access3-share"
    submodules = True
    maintainers("anton-seaice", "harshula", "micaeljtoliveira")
    license("Apache-2.0", checked_by="anton-seaice")

    variant(
        "configurations",
        values=(*KNOWN_CONF, 'none'),
        default='none',
        multi=True,
        description=(
            "ACCESS-OM3 configurations to build. When a model component "
            "is not included in a configuration, that component is replaced by "
            "a CDEPS data component."
        ),
        sticky=True  # force concretizer to not pick alternative variants
    )

    # force user to supply a build combination
    conflicts(
        "configurations=none",
        msg=f"A configurations variant must be set, can be one or many of {KNOWN_CONF}"
    )

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("access3-share")
    depends_on("esmf@8.7.0:")

    for conf in KNOWN_CONF:
        if "CICE6" in conf:
            depends_on("access-cice+access3", when=f"configurations={conf}")
        if "MOM6" in conf:
            depends_on("access-mom6+access3", when=f"configurations={conf}")
        if "WW3" in conf:
            depends_on("access-ww3+access3", when=f"configurations={conf}")

    flag_handler = build_system_flags

    def cmake_args(self):
        # make configurations a cmake argument
        buildConf = ";".join(self.spec.variants["configurations"].value)

        args = [
            self.define("BuildConfigurations", buildConf),
            self.define("ACCESS3_LIB_INSTALL", False),
        ]

        return args
