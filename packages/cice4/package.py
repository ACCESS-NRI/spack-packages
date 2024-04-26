# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import install, join_path, mkdirp

# https://spack.readthedocs.io/en/latest/build_systems/makefilepackage.html
class Cice4(MakefilePackage):
    """The Los Alamos sea ice model (CICE) is the result of an effort to develop a computationally efficient sea ice component for a fully coupled atmosphere-land global climate model."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/cice4.git"

    maintainers("penguian")

    version("master", branch="ESM_1.5")

    # Depend on virtual package "mpi".
    depends_on("mpi")
    depends_on("netcdf-fortran@4.5.2:")
    depends_on("netcdf-c@4.7.1:")
    depends_on("oasis3-mct")

    phases = ["edit", "build", "install"]

    _buildscript = "spack-build.sh"
    _buildscript_path = join_path("bld", _buildscript)

    # The integer represents environment variable NTASK
    __targets = {12: {},}
    __targets[12]["driver"] = "access"
    __targets[12]["grid"] = "360x300"
    __targets[12]["blocks"] = "12x1"

    # Comment from cice4/compile/comp_access-cm_cice.RJ.nP-mct:
    # Recommendations:
    #   NTASK equals nprocs in ice_in
    #   use processor_shape = slenderX1 or slenderX2 in ice_in
    #   one per processor with distribution_type='cartesian' or
    #   squarish blocks with distribution_type='rake'
    # If BLCKX (BLCKY) does not divide NXGLOB (NYGLOB) evenly, padding
    # will be used on the right (top) of the grid.

    # The reason for the explicit -rpath is:
    # https://github.com/ACCESS-NRI/spack_packages/issues/14#issuecomment-1653651447
    def get_linker_args(self, spec, name):
        return " ".join(
                    [(spec[name].libs).ld_flags,
                    "-Wl,-rpath=" + join_path(spec[name].prefix, "lib")]
                   )

    # The reason for the explicit -rpath is:
    # https://github.com/ACCESS-NRI/spack_packages/issues/14#issuecomment-1653651447
    def make_linker_args(self, spec, name, namespecs):
        path = join_path(spec[name].prefix, "lib")
        return " ".join(
                    ["-L" + path,
                    namespecs,
                    "-Wl,-rpath=" + path]
                   )

    def edit(self, spec, prefix):

        srcdir = self.stage.source_path
        buildscript_dest = join_path(srcdir, self._buildscript_path)
        makeinc_path = join_path(srcdir, "bld", "Macros.spack")

        copy(join_path(self.package_dir, self._buildscript), buildscript_dest)

        config = {}

        istr = join_path((spec["oasis3-mct"].headers).cpp_flags, "psmile.MPI1")
        ideps = ["oasis3-mct", "netcdf-fortran"]
        incs = " ".join([istr] + [(spec[d].headers).cpp_flags for d in ideps])

        lstr = ""
        ldeps = ["oasis3-mct", "netcdf-c", "netcdf-fortran"]
        libs = " ".join([lstr] + [self.get_linker_args(spec, d) for d in ldeps])

        CFLAGS = "-c -O2"

        # Copied from access-esm-build-gadi/patch/Macros.Linux.raijin.nci.org.au-mct
        config["pre"] = f"""
INCLDIR    := -I. {incs}
SLIBS      := {libs}
ULIBS      :=
CPP        := cpp
FC         := mpif90

CPPFLAGS   := -P -traditional
CPPDEFS    := -DLINUX -DPAROPT
CFLAGS     := {CFLAGS}
FIXEDFLAGS := -132
FREEFLAGS  :=
"""

        config["gcc"] = f"""
FFLAGS = -Wall -fdefault-real-8 -fdefault-double-8 -ffpe-trap=invalid,zero,overflow -fallow-argument-mismatch
LDFLAGS    := $(FFLAGS)
"""

        config["intel"] = f"""
ifeq ($(DEBUG), yes)
    FFLAGS     := -r8 -i4 -O0 -g -align all -w -ftz -convert big_endian -assume byterecl -no-vec -xHost -fp-model precise
else
    FFLAGS     := -r8 -i4 -O2 -align all -w -ftz -convert big_endian -assume byterecl -no-vec -xHost -fp-model precise
endif
LDFLAGS    := $(FFLAGS) -v -static-intel 
"""

        # Copied from bld/Macros.nci
        config["post"] = """
MOD_SUFFIX := mod
LD         := $(FC)

    CPPDEFS :=  $(CPPDEFS) -DNXGLOB=$(NXGLOB) -DNYGLOB=$(NYGLOB) -DN_ILYR=$(N_ILYR) \
                -DBLCKX=$(BLCKX) -DBLCKY=$(BLCKY) -DMXBLCKS=$(MXBLCKS)

ifeq ($(DITTO), yes)
   CPPDEFS :=  $(CPPDEFS) -DREPRODUCIBLE
endif

ifeq ($(NETCDF), yes)
   CPPDEFS :=  $(CPPDEFS) -Dncdf
endif

ifeq ($(USE_ESMF), yes)
   CPPDEFS :=  $(CPPDEFS) -Duse_esmf
endif

ifeq ($(AusCOM), yes)
   CPPDEFS := $(CPPDEFS) -DAusCOM -Dcoupled
endif

ifeq ($(ACCESS), yes)
   CPPDEFS := $(CPPDEFS) -DACCESS
endif

ifeq ($(OASIS3_MCT), yes)
   CPPDEFS := $(CPPDEFS) -DOASIS3_MCT
endif
"""
        fullconfig = config["pre"] + config[self.compiler.name] + config["post"]
        print(fullconfig)
        with open(makeinc_path, "w") as makeinc:
            makeinc.write(fullconfig)

    def build(self, spec, prefix):

        build = Executable(
                    join_path(self.stage.source_path, self._buildscript_path)
                )

        for k in self.__targets:
            build(self.__targets[k]["driver"],
                    self.__targets[k]["grid"],
                    self.__targets[k]["blocks"],
                    str(k))

    def install(self, spec, prefix):

        mkdirp(prefix.bin)
        for k in self.__targets:
            name = "_".join([self.__targets[k]["driver"],
                                self.__targets[k]["grid"],
                                self.__targets[k]["blocks"],
                                str(k) + "p"])
            install(join_path("build_" + name, "cice_" + name + ".exe"),
                    prefix.bin)
