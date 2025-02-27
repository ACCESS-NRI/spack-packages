# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0 

from spack.package import *
from spack.variant import any_combination_of

class Access3Exe(CMakePackage):
    """Executable build for ACCESS version 3 climate models. The exectuable is defined in Community Mediator for Earth Prediction 
    Systems (CMEPS). Currently implemented for ACCESS-OM3, and in the future may support ACCESS-CM3 and ACCESS-ESM3. This is a 
    companion pacakge to Access3Share which builds the shared libraries."""

    homepage = "https://github.com/ACCESS-NRI/access3-share"
    git = "https://github.com/ACCESS-NRI/access3-share"
    submodules = True
    maintainers = ["anton-seaice", "harshula", "micaeljtoliveira"]

    license("Apache-2.0", checked_by="anton-seaice")

    variant(
        "configurations",
        # default="MOM6-CICE6, CICE6-WW3, MOM6-CICE6-WW3", if we set these defaults there is no way to unset them in the deployment
        # default="CICE6",
        values=any_combination_of(
            "MOM6",
            "CICE6",
            "WW3",
            "MOM6-WW3",
            "MOM6-CICE6",
            "CICE6-WW3",
            "MOM6-CICE6-WW3",
        ).prohibit_empty_set().with_error("at least one configuration to build is required (e.g. MOM6-CICE6)"),
        # multi=True,
        description="ACCESS-OM3 configurations to build",
    )
    
    variant("openmp", default=False, description="Enable OpenMP")
    
    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")

    for configurations in ["CICE6", "MOM6-CICE6", "MOM6-CICE6-WW3", "CICE6-WW3"]:
        depends_on("access-cice+cesmcoupled+access3")
    for configurations in ["MOM6", "MOM6-CICE6", "MOM6-CICE6-WW3", "MOM6-WW3"]:
        depends_on("access-mom6+cesmcoupled+access3")
    # for configurations in ["WW3", "CICE6-WW3", "MOM6-CICE6-WW3", "MOM6-WW3"]:
        # depends_on("access-ww3 driver=nuopc/cmeps +cesmcoupled")
    
    flag_handler = CMakePackage.build_system_flags

    def cmake_args(self):

        # make configurations a cmake argument
        buildConf = ";".join(self.spec.variants["configurations"].value)
        args = [
            self.define("BuildConfigurations",buildConf)
        ]
        
        return args
