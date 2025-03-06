# Copyright 2013-2025 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0 

from spack.package import *
from spack.variant import disjoint_sets, auto_or_any_combination_of

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

DEFAULT_CONF = ("MOM6", "MOM6-CICE6", "MOM6-CICE6-WW3")

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
        values=any_combination_of(*KNOWN_CONF), 
        description="ACCESS-OM3 configurations to build",
        sticky=True #force concretizer to not pick alternative variants
    )
    
    variant("openmp", default=False, description="Enable OpenMP")
    
    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("esmf@8.3.0:")
    depends_on("esmf cflags='-fp-model precise' fflags='-fp-model precise'", when="%intel")
    depends_on("esmf cflags='-fp-model precise' fflags='-fp-model precise'", when="%oneapi")

    depends_on("access-cice+access3+cesmcoupled", when="configurations=CICE6")
    depends_on("access-cice+access3+cesmcoupled", when="configurations=CICE6-WW3")
    depends_on("access-cice+access3+cesmcoupled", when="configurations=MOM6-CICE6")
    depends_on("access-cice+access3+cesmcoupled", when="configurations=MOM6-CICE6-WW3")
    depends_on("access-cice+access3+cesmcoupled", when="configurations=none")

    depends_on("access-mom6+access3+cesmcoupled", when="configurations=MOM6")
    depends_on("access-mom6+access3+cesmcoupled", when="configurations=MOM6-CICE6")
    depends_on("access-mom6+access3+cesmcoupled", when="configurations=MOM6-WW3")
    depends_on("access-mom6+access3+cesmcoupled", when="configurations=MOM6-CICE6-WW3")
    depends_on("access-mom6+access3+cesmcoupled", when="configurations=none")

    # depends_on("access-ww3+access3+cesmcoupled", when="configurations=WW3")
    # depends_on("access-ww3+access3+cesmcoupled", when="configurations=MOM6-WW3")
    # depends_on("access-ww3+access3+cesmcoupled", when="configurations=CICE6-WW3")
    # depends_on("access-ww3+access3+cesmcoupled", when="configurations=MOM6-CICE6-WW3")
    # depends_on("access-ww3+access3+cesmcoupled", when="configurations=none")
   
    def cmake_args(self):

        # make configurations a cmake argument
        if self.spec.satisfies("configurations=none"):
            buildConf = ";".join(DEFAULT_CONF)
        else:
            buildConf = ";".join(self.spec.variants["configurations"].value)
        
        args = [
            self.define("BuildConfigurations",buildConf)
        ]
        
        return args
