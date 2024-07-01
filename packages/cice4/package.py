# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# Based on packages/cice5/package.py and other sources noted below.

from spack.package import install, join_path, mkdirp

# https://spack.readthedocs.io/en/latest/build_systems/makefilepackage.html
class Cice4(MakefilePackage):
    """The Los Alamos sea ice model (CICE) is the result of an effort to develop a computationally efficient sea ice component for a fully coupled atmosphere-land global climate model."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/cice4.git"

    maintainers("penguian")

    version("access-esm1.5", branch="access-esm1.5")

    depends_on("netcdf-fortran@4.5.1:4.5.2")
    # Depend on "openmpi".
    depends_on("openmpi@4.0.2:4.1.0")
    depends_on("oasis3-mct@access-esm1.5")

    phases = ["edit", "build", "install"]

    _buildscript = "spack-build.sh"
    _buildscript_path = join_path("bld", _buildscript)

    # The integer represents environment variable NTASK
    __targets = {12: {}, }
    __targets[12]["driver"] = "access"
    __targets[12]["grid"] = "360x300"
    __targets[12]["blocks"] = "12x1"

    # The reason for the explicit -rpath is:
    # https://github.com/ACCESS-NRI/spack_packages/issues/14#issuecomment-1653651447
    def get_linker_args(self, spec, name):
        return " ".join(
                    [(spec[name].libs).ld_flags,
                    "-Wl,-rpath=" + join_path(spec[name].prefix, "lib")]
                   )

    def edit(self, spec, prefix):

        srcdir = self.stage.source_path
        buildscript_dest = join_path(srcdir, self._buildscript_path)
        makeinc_path = join_path(srcdir, "bld", "Macros.spack")

        copy(join_path(self.package_dir, self._buildscript), buildscript_dest)

        config = {}

        istr = " ".join([
                join_path((spec["oasis3-mct"].headers).cpp_flags, "psmile.MPI1"),
                join_path((spec["oasis3-mct"].headers).cpp_flags, "mct")])
        ideps = ["netcdf-fortran"]
        incs = " ".join([istr] + [(spec[d].headers).cpp_flags for d in ideps])

        lstr = ""
        ldeps = ["oasis3-mct", "netcdf-fortran"]
        libs = " ".join([lstr] + [self.get_linker_args(spec, d) for d in ldeps])

        CFLAGS = "-c -O2"

        # Based on https://github.com/coecms/access-esm-build-gadi/blob/master/patch/Macros.Linux.raijin.nci.org.au-mct
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

        # based on packages/cice5/package.py (FFLAGS)
        # and  https://github.com/coecms/access-esm-build-gadi/blob/master/patch/Macros.Linux.raijin.nci.org.au-mct (LDFLAGS)
        config["gcc"] = """
FFLAGS = -Wall -fdefault-real-8 -fdefault-double-8 -ffpe-trap=invalid,zero,overflow -fallow-argument-mismatch
LDFLAGS    := $(FFLAGS)
"""

        # Based on https://github.com/coecms/access-esm-build-gadi/blob/master/patch/Macros.Linux.raijin.nci.org.au-mct
        config["intel"] = """
ifeq ($(DEBUG), yes)
    FFLAGS     := -r8 -i4 -O0 -g -align all -w -ftz -convert big_endian -assume byterecl -no-vec -xCORE-AVX2 -fp-model precise
else
    FFLAGS     := -r8 -i4 -O2 -align all -w -ftz -convert big_endian -assume byterecl -no-vec -xCORE-AVX512 -fp-model precise
endif
LDFLAGS    := $(FFLAGS) -v -static-intel 
"""

        # Add support for the ifx compiler
        config["oneapi"] = config["intel"]

        # Based on https://github.com/ACCESS-NRI/cice4/blob/access-esm1.5/bld/Macros.nci
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

ifeq ($(UNIT_TESTING), yes)
   CPPDEFS := $(CPPDEFS) -DUNIT_TESTING
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
