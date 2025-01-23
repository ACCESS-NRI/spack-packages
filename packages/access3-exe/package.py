# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0 

from spack.package import *


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
        "build_type",
        default="Release",
        description="The build type to build",
        values=("Debug", "Release"),
    )

    # To-DO: confirm if we want a MOM6 only for regional modelling
    variant(
        "configurations",
        # default="MOM6-CICE6, CICE6-WW3, MOM6-CICE6-WW3", if we set these defaults there is no way to unset them in the deployment
        default="CICE6",
        values=(
            "MOM6",
            "CICE6",
            "WW3",
            "MOM6-WW3",
            "MOM6-CICE6",
            "CICE6-WW3",
            "MOM6-CICE6-WW3",
        ),
        multi=True,
        description="ACCESS-OM3 configurations to build",
    )
    
    variant("openmp", default=False, description="Enable OpenMP")
    
    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("access-cice+cesmcoupled+access3")
    depends_on("access-mom6+cesmcoupled+access3")
    # depends_on("access-ww3 driver=nuopc/cmeps +cesmcoupled")
    
    flag_handler = CMakePackage.build_system_flags

    def cmake_args(self):

        args = [
            self.define_from_variant("OPENMP", "openmp"),
            self.define(
                "ENABLE_MOM6", "configurations=MOM6" in self.spec
            ),
            self.define(
                "ENABLE_CICE6", "configurations=CICE6" in self.spec
            ),
            self.define(
                "ENABLE_WW3", "configurations=WW3" in self.spec
            ),
            self.define(
                "ENABLE_MOM6-WW3", "configurations=MOM6-WW3" in self.spec
            ),
            self.define(
                "ENABLE_MOM6-CICE6", "configurations=MOM6-CICE6" in self.spec
            ),
            self.define(
                "ENABLE_CICE6-WW3", "configurations=CICE6-WW3" in self.spec
            ),
            self.define(
                "ENABLE_MOM6-CICE6-WW3", "configurations=MOM6-CICE6-WW3" in self.spec
            ),
        ]

        # we need this for cmake to find MPI_Fortran
        args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))
        
        return args
