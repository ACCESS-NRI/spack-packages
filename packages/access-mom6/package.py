# Copyright 2013-2025 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0
# ----------------------------------------------------------------------------

from spack.package import CMakePackage, variant, version, depends_on


class AccessMom6(CMakePackage):
    """The Modular Ocean Model (MOM) describes the numerical ocean models originating from NOAA/GFDL. 
    They are used to simulate ocean currents at both regional and global scales, 
    enabling scientists to answer fundamental questions about the role of the ocean in the dynamics of the global climate.
    This package builds using the Access3Share common libraries for ACCESS 3 models."""

    homepage = "https://github.com/ACCESS-NRI/MOM6"
    git = "https://github.com/ACCESS-NRI/MOM6.git"
    submodules = True
    maintainers("minghangli-uni", "harshula")
    
    # see license file in https://github.com/ACCESS-NRI/MOM6/blob/e92c971084e185cfd3902f18072320b45d583a54/LICENSE.md
    license("LGPL-3.0", checked_by="minghangli-uni")

    variant("openmp", default=False, description="Enable OpenMP")
    variant("mom_symmetric", default=False, description="Use symmetric memory in MOM6")
    variant("access3", default=True, description="Building MOM6 library with Access3share")
    variant("cesmcoupled", default=False, description="Enable parameters with cesm coupled")

    depends_on("access3-share", when="+access3")
    depends_on("access3-share+openmp", when="+openmp+access3")

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")
    depends_on("fms@2021.03: build_type==RelWithDebInfo precision=64 +large_file ~gfs_phys ~quad_precision")
    depends_on("fms +openmp", when="+openmp")
    depends_on("fms ~openmp", when="~openmp")

    root_cmakelists_dir = "cmake"

    def cmake_args(self):
        args = [
            self.define_from_variant("OPENMP", "openmp"),
            self.define_from_variant("ENABLE_MOM_SYMMETRIC", "mom_symmetric"),
            self.define_from_variant("ACCESS3_MOM6", "access3"),
            self.define_from_variant("CESMCOUPLED", "cesmcoupled"),
        ]

        return args
