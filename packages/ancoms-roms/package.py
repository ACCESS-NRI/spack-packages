# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os
import sys

from spack.package import *


class AncomsRoms(MakefilePackage):
    """ROMS is a free-surface, terrain-following,
    primitive equations ocean model widely used by
    the scientific community for a diverse range of applications"""

    homepage = "https://www.myroms.org/"
    git = "https://github.com/ACCESS-Community-Hub/roms.git"
    url = "https://github.com/ACCESS-Community-Hub/roms/archive/refs/tags/roms-4.1.tar.gz"

    version("unsw", branch="unsw-coastal-regional-lab", preferred=True)

    variant("openmp", default=False, description="Turn on shared-memory parallelization in ROMS")
    variant("mpi", default=True, description="Turn on distributed-memory parallelization in ROMS")
    variant(
        "roms_application",
        default="benchmark",
        description="Makefile to include its associated header file",
        values=("upwelling", "benchmark"),
        multi=False,
    )
    variant(
        "debug",
        default=False,
        description="Turn on symbolic debug information with no optimization",
    )

    depends_on("mpi", when="+mpi")
    depends_on("netcdf-fortran")
    depends_on("netcdf-c")
    depends_on("hdf5+fortran")
    depends_on("zlib-api")
    depends_on("curl")
    depends_on("amdlibm", when="%aocc")

    # Note: you cannot set USE_OpenMP and USE_MPI at the same time
    conflicts("+mpi+openmp")

    def _copy_arch_file(self, lib):
        """AOCC compiler takes gfortran's makefile as reference"""
        copy(
            join_path("Compilers", "Linux-gfortran.mk"),
            join_path("Compilers", "{0}-{1}.mk".format(self.arch, lib)),
        )

    @property
    def selected_roms_application(self):
        """
        Application type that have been selected in this build
        """
        return self.spec.variants["roms_application"].value

    @property
    def arch(self):
        """return target platform"""
        plat = sys.platform
        if plat.startswith("linux"):
            plat = "Linux"
        return plat

    def _edit_arch(self, spec, prefix, lib):
        """
        Edit Linux-flang.mk makefile to support AOCC compiler
        """
        fflags = ["-fveclib=AMDLIBM", "-O3", "-ffast-math", "-funroll-loops", "-std=f2008"]
        make_aocc = join_path("Compilers", "{0}-{1}.mk".format(self.arch, lib))

        filter_file(r"\sFC := gfortran*$", " FC := {0}".format(lib), make_aocc)
        filter_file(r"\sFFLAGS :=.*$", " FFLAGS := {0}".format(" ".join(fflags)), make_aocc)
        filter_file("-fallow-argument-mismatch", "", make_aocc, string=True)
        filter_file(
            r"\sLIBS :=.*", " LIBS := {0}".format(spec["amdlibm"].libs.ld_flags), make_aocc
        )
        filter_file(r"\sFREEFLAGS :=.*", " FREEFLAGS := -ffree-form", make_aocc)

    def edit(self, spec, prefix):
        # ROMS doesn't have support for AOCC out of the box
        # Support extended to AOCC from below steps
        if "%aocc" in self.spec:
            lib_info = os.path.basename(spack_fc)
            self._copy_arch_file(lib_info)
            self._edit_arch(spec, prefix, lib_info)

        # With gfortran >= 10 requires '-fallow-argument-mismatch' flag
        if spec.satisfies("@:4.0 %gcc@10:"):
            filter_file(
                r"\sFFLAGS := ",
                " FFLAGS := -fallow-argument-mismatch ",
                "Compilers/Linux-gfortran.mk",
            )

        makefile = FileFilter("makefile")

        app_type = self.selected_roms_application

        makefile.filter(
            r"ROMS_APPLICATION.*?=.*", "ROMS_APPLICATION = {0}".format(app_type.upper())
        )
        makefile.filter(r"\sFORT\s[?]=.*", "FORT = {0}".format(os.path.basename(spack_fc)))
        makefile.filter(r"\sUSE_NETCDF4\s[?]=.*", "USE_NETCDF4 = on")

        # Build MPI variant of ROMS
        if "+mpi" in self.spec:
            makefile.filter(r"\sUSE_MPI\s[?]=.*", "USE_MPI = on")
            makefile.filter(r"\sUSE_MPIF90\s[?]=.*", "USE_MPIF90 = on")
            makefile.filter(r"\sUSE_OpenMP\s[?]=.*", "USE_OpenMP =")

        # Build OpenMP variant of ROMS
        if "+openmp" in self.spec:
            makefile.filter(r"\sUSE_OpenMP\s[?]=.*", "USE_OpenMP = on")
            makefile.filter(r"\sUSE_MPI\s[?]=.*", "USE_MPI =")
            makefile.filter(r"\sUSE_MPIF90\s[?]=.*", "USE_MPIF90 =")

        # Build Debug variant of ROMS
        if "+debug" in self.spec:
            makefile.filter(r"\sUSE_DEBUG\s[?]=.*", "USE_DEBUG = on")

    def setup_build_environment(self, env):
        spec = self.spec

        netcdf_include = spec["netcdf-fortran"].prefix.include
        nf_config = join_path(spec["netcdf-fortran"].prefix.bin, "nf-config")

        env.set("NF_CONFIG", nf_config)
        env.set("NETCDF_INCDIR", netcdf_include)
        env.set("HDF5_INCDIR", spec["hdf5"].prefix.include)
        env.set("HDF5_LIBDIR", spec["hdf5"].prefix.libs)

    def build(self, spec, prefix):
        make(parallel=False)

    def install(self, spec, prefix):
        mkdirp(prefix.bin)
        # Keep ROMS External Standard input scripts
        mkdirp(spec.prefix.ROMS)

        install("roms*", prefix.bin)
        install_tree("./ROMS/External", join_path(spec.prefix.ROMS.External))
