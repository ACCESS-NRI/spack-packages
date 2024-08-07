# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import CMakePackage, variant, version, depends_on

class AccessOm3Nuopc(CMakePackage):
    """ACCESS-OM3 global ocean-sea ice-wave coupled model."""

    homepage = "https://www.github.com/COSIMA/access-om3"
    git = "https://github.com/COSIMA/access-om3.git"
    submodules = True
    maintainers = ["micaeljtoliveira", "aekiss"]

    version("main", branch="main", submodules=True)

    variant(
        "build_type",
        default="Release",
        description="The build type to build",
        values=("Debug", "Release"),
    )
    variant(
        "configurations",
        default="MOM6-CICE6, CICE6-WW3, MOM6-CICE6-WW3",
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
    variant(
        "install_libraries",
        default=False,
        description="Install component libraries"
    )
    variant("openmp", default=False, description="Enable OpenMP")
    variant("mom_symmetric", default=False, description="Use symmetric memory in MOM6")
    variant(
        "cice_io",
        default="PIO",
        description="CICE IO option",
        values=("NectCDF", "PIO", "Binary"),
        multi=False,
    )

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")
    depends_on("esmf@8.3.0:")
    depends_on("esmf cflags='-fp-model precise' fflags='-fp-model precise'", when="%intel")
    depends_on("fortranxml@4.1.2:")
    depends_on("fms@2021.03: build_type==RelWithDebInfo precision=64 +large_file ~gfs_phys ~quad_precision")
    depends_on("fms +openmp", when="+openmp")
    depends_on("fms ~openmp", when="~openmp")

    depends_on("parallelio@2.5.10: build_type==RelWithDebInfo")
    depends_on("parallelio fflags='-qno-opt-dynamic-align -convert big_endian -assume byterecl -ftz -traceback -assume realloc_lhs -fp-model source' cflags='-qno-opt-dynamic-align -fp-model precise -std=gnu99'", when="%intel")

    flag_handler = CMakePackage.build_system_flags

    def cmake_args(self):
        args = [
            self.define_from_variant("OM3_MOM_SYMMETRIC", "mom_symmetric"),
            self.define_from_variant("OM3_LIB_INSTALL", "install_libraries"),
            self.define_from_variant("OM3_OPENMP", "openmp"),
            self.define(
                "OM3_ENABLE_MOM6", "configurations=MOM6" in self.spec
            ),
            self.define(
                "OM3_ENABLE_CICE6", "configurations=CICE6" in self.spec
            ),
            self.define(
                "OM3_ENABLE_WW3", "configurations=WW3" in self.spec
            ),
            self.define(
                "OM3_ENABLE_MOM6-WW3", "configurations=MOM6-WW3" in self.spec
            ),
            self.define(
                "OM3_ENABLE_MOM6-CICE6", "configurations=MOM6-CICE6" in self.spec
            ),
            self.define(
                "OM3_ENABLE_CICE6-WW3", "configurations=CICE6-WW3" in self.spec
            ),
            self.define(
                "OM3_ENABLE_MOM6-CICE6-WW3",
                "configurations=MOM6-CICE6-WW3" in self.spec
            ),
        ]

        args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))

        return args
