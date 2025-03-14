# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class AccessWw3(CMakePackage):
    """WAVEWATCH III® is a community wave modeling framework that includes the latest 
    scientific advancements in the field of wind-wave modeling and dynamics. 
    This package builds using the Access3Share common libraries for ACCESS 3 models."""

    homepage = "https://github.com/noaa-emc/ww3/"
    git = "https://github.com/ACCESS-NRI/WW3"
    maintainers("anton-seaice", "harshula")
    
    license("LGPL-3.0", checked_by="anton-seaice")

    variant("openmp", default=False, description="Enable OpenMP")
    variant("access3", default=True, description="Install CICE as library for Access3 models") 
    variant("cesmcoupled", default=False, description="Set CESMCOUPLED CPP Flag")

    depends_on("access3-share", when="+access3") 

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")   
    
    def cmake_args(self):
        args = [
            self.define_from_variant("OPENMP", "openmp"),
            self.define_from_variant("ACCESS3_WW3", "access3"),
            self.define_from_variant("CESMCOUPLED", "cesmcoupled"),
        ]

        # args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        # args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        # args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))
        
        return args