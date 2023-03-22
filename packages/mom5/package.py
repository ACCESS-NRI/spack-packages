# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import install, join_path, mkdirp

# https://spack.readthedocs.io/en/latest/build_systems/makefilepackage.html
class Mom5(MakefilePackage):
    """MOM is a numerical ocean model based on the hydrostatic primitive equations."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/mom5.git"
    # NOTE: URL definition required for CI
    # Spack needs tarball URL to be defined to access github branches
    url = "https://github.com/ACCESS-NRI/mom5/tarball/master"

    maintainers = ["harshula"]

    version("master", branch="master")

    # Depend on virtual package "mpi".
    depends_on("mpi")
    depends_on("oasis3-mct")
    depends_on("datetime-fortran")
    depends_on("netcdf-fortran@4.5.2:")
    depends_on("netcdf-c@4.7.4:")
    # TODO: For initial verification we are going to use static pio.
    #       Eventually we plan to move to shared pio
    # ~shared requires: https://github.com/spack/spack/pull/34837
    depends_on("parallelio~pnetcdf~timing~shared")
    depends_on("libaccessom2")

    phases = ["edit", "build", "install"]

    _platform = "spack"
    _mom_type = "ACCESS-OM"

    def edit(self, spec, prefix):

        srcdir = self.stage.source_path
        makeinc_path = join_path(srcdir, "bin", "mkmf.template.spack")
        config = {}

        istr = join_path((spec["oasis3-mct"].headers).cpp_flags, "psmile.MPI1")
        ideps = ["parallelio", "oasis3-mct", "libaccessom2", "netcdf-fortran"]
        incs = " ".join([istr] + [(spec[d].headers).cpp_flags for d in ideps])

        lstr = " ".join(
                    ["".join(["-L", join_path(spec["parallelio"].prefix, "lib")]),
                    "-lpiof",
                    "-lpioc"]
                   )
        # NOTE: The order of the libraries matter during the linking step!
        # NOTE: datetime-fortran is a dependency of libaccessom2.
        ldeps = ["oasis3-mct", "libaccessom2", "netcdf-c", "netcdf-fortran", "datetime-fortran"]
        libs = " ".join([lstr] + [(spec[d].libs).ld_flags for d in ldeps])

        # Copied from bin/mkmf.template.ubuntu
        config["gcc"] = f"""
FC = mpifort
CC = gcc
LD = $(FC)
#########
# flags #
#########
DEBUG =
REPRO =
VERBOSE =
OPENMP =

MAKEFLAGS += --jobs=$(shell grep '^processor' /proc/cpuinfo | wc -l)

FPPFLAGS := 

FFLAGS := -fcray-pointer -fdefault-real-8 -ffree-line-length-none -fno-range-check -Waliasing -Wampersand -Warray-bounds -Wcharacter-truncation -Wconversion -Wline-truncation -Wintrinsics-std -Wsurprising -Wno-tabs -Wunderflow -Wunused-parameter -Wintrinsic-shadow -Wno-align-commons -fallow-argument-mismatch -fallow-invalid-boz
FFLAGS += {incs}
FFLAGS += -DGFORTRAN

#
FFLAGS_OPT = -O2
FFLAGS_REPRO = 
FFLAGS_DEBUG = -O0 -g -W -fbounds-check 
FFLAGS_OPENMP = -fopenmp
FFLAGS_VERBOSE = 

CFLAGS := -D__IFC {incs}
CFLAGS += $(shell nc-config --cflags)
CFLAGS_OPT = -O2
CFLAGS_OPENMP = -fopenmp
CFLAGS_DEBUG = -O0 -g 

# Optional Testing compile flags.  Mutually exclusive from DEBUG, REPRO, and OPT
# *_TEST will match the production if no new option(s) is(are) to be tested.
FFLAGS_TEST = -O2
CFLAGS_TEST = -O2

LDFLAGS :=
LDFLAGS_OPENMP := -fopenmp
LDFLAGS_VERBOSE := 

ifneq ($(REPRO),)
CFLAGS += $(CFLAGS_REPRO)
FFLAGS += $(FFLAGS_REPRO)
endif
ifneq ($(DEBUG),)
CFLAGS += $(CFLAGS_DEBUG)
FFLAGS += $(FFLAGS_DEBUG)
else ifneq ($(TEST),)
CFLAGS += $(CFLAGS_TEST)
FFLAGS += $(FFLAGS_TEST)
else
CFLAGS += $(CFLAGS_OPT)
FFLAGS += $(FFLAGS_OPT)
endif

ifneq ($(OPENMP),)
CFLAGS += $(CFLAGS_OPENMP)
FFLAGS += $(FFLAGS_OPENMP)
LDFLAGS += $(LDFLAGS_OPENMP)
endif

ifneq ($(VERBOSE),)
CFLAGS += $(CFLAGS_VERBOSE)
FFLAGS += $(FFLAGS_VERBOSE)
LDFLAGS += $(LDFLAGS_VERBOSE)
endif

ifeq ($(NETCDF),3)
  # add the use_LARGEFILE cppdef
  ifneq ($(findstring -Duse_netCDF,$(CPPDEFS)),)
    CPPDEFS += -Duse_LARGEFILE
  endif
endif

LIBS := {libs}
LDFLAGS += $(LIBS)
"""

        # Copied from bin/mkmf.template.nci
        config["intel"] = f"""
ifeq ($(VTRACE), yes)
    FC := mpifort-vt
    LD := mpifort-vt
else
    FC := mpifort
    LD := mpifort
endif

CC := mpicc

VERBOSE :=
OPT := on

MAKEFLAGS += -j

INCLUDE   := {incs}

FPPFLAGS := -fpp -Wp,-w $(INCLUDE)
FFLAGS := -fno-alias -safe-cray-ptr -fpe0 -ftz -assume byterecl -i4 -r8 -traceback -nowarn -check noarg_temp_created -assume nobuffered_io -convert big_endian -grecord-gcc-switches -align all
FFLAGS_OPT := -g3 -O2 -xCORE-AVX2 -debug all -check none
FFLAGS_REPORT := -qopt-report=5 -qopt-report-annotate
FFLAGS_DEBUG := -g3 -O0 -debug all -check -check noarg_temp_created -check nopointer -warn -warn noerrors -ftrapuv
FFLAGS_REPRO := -fp-model precise -fp-model source -align all
FFLAGS_VERBOSE := -v -V -what

CFLAGS := -D__IFC $(INCLUDE)
CFLAGS_OPT := -O2 -debug minimal -xCORE-AVX2
CFLAGS_REPORT := -qopt-report=5 -qopt-report-annotate
CFLAGS_DEBUG := -O0 -g -ftrapuv -traceback
CFLAGS_REPRO := -fp-model precise -fp-model source

LDFLAGS :=
LDFLAGS_VERBOSE := -Wl,-V,--verbose,-cref,-M

ifneq ($(REPRO),)
CFLAGS += $(CFLAGS_REPRO)
FFLAGS += $(FFLAGS_REPRO)
endif

ifneq ($(DEBUG),)
CFLAGS += $(CFLAGS_DEBUG)
FFLAGS += $(FFLAGS_DEBUG)
else
CFLAGS += $(CFLAGS_OPT)
FFLAGS += $(FFLAGS_OPT)
endif

ifneq ($(VERBOSE),)
CFLAGS += $(CFLAGS_VERBOSE)
FFLAGS += $(FFLAGS_VERBOSE)
LDFLAGS += $(LDFLAGS_VERBOSE)
endif

ifneq ($(REPORT),)
CFLAGS += $(CFLAGS_REPORT)
FFLAGS += $(FFLAGS_REPORT)
endif

LIBS := {libs}

ifneq ($(OASIS_ROOT),)
LIBS += -L$(OASIS_ROOT)/Linux/lib -lpsmile.MPI1 -lmct -lmpeu -lscrip
endif

ifneq ($(LIBACCESSOM2_ROOT),)
LIBS += -L$(LIBACCESSOM2_ROOT)/build/lib -laccessom2
endif

LDFLAGS += $(LIBS)
"""

        # Copied from bin/mkmf.template.t90
        config["post"] = """
# you should never need to change any lines below.

# see the CF90 manual for more details on some of the file extensions
# discussed here.
# this makefile template recognizes fortran sourcefiles with extensions
# .f, .f90, .F, .F90. Given a sourcefile <file>.<ext>, where <ext> is one of
# the above, this provides a number of default actions:

# make <file>.T		create a CIF file
# make <file>.lst	create a compiler listing
# make <file>.o		create an object file
# make <file>.s		create an assembly listing
# make <file>.x		create an executable file, assuming standalone
#			source

# make <file>.i		create a preprocessed file (only for .F and .F90
#			extensions)

# make <file>.hpm	produce hpm output from <file>.x
# make <file>.proc	produce procstat output from <file>.x

# The macro TMPFILES is provided to slate files like the above for removal.

RM = rm -f
SHELL = /bin/csh
TMPFILES = .*.m *.T *.TT *.hpm *.i *.lst *.proc *.s

.SUFFIXES: .F .F90 .H .T .f .F90 .h .hpm .i .lst .proc .o .s .x

.f.T:
	$(FC) $(FFLAGS) -c -Ca $*.f
.f.lst:
	$(FC) $(FFLAGS) $(LIST) -c $*.f
.f.o:
	$(FC) $(FFLAGS) -c     $*.f
.f.s:
	$(FC) $(FFLAGS) -eS    $*.f
.f.x:
	$(FC) $(FFLAGS) $(LDFLAGS) -o $*.x $*.f
.f90.T:
	$(FC) $(FFLAGS) -c -Ca $*.f90
.f90.lst:
	$(FC) $(FFLAGS) $(LIST) -c $*.f90
.f90.o:
	$(FC) $(FFLAGS) -c     $*.f90
.f90.s:
	$(FC) $(FFLAGS) -c -eS $*.f90
.f90.x:
	$(FC) $(FFLAGS) $(LDFLAGS) -o $*.x $*.f90
.F.T:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c -Ca $*.F
.F.i:
	$(FC) $(CPPDEFS) $(CPPFLAGS) -eP $*.F
.F.lst:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) $(LIST) -c $*.F
.F.o:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c     $*.F
.F.s:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c -eS $*.F
.F.x:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) $(LDFLAGS) -o $*.x $*.F
.F90.T:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c -Ca $*.F90
.F90.i:
	$(FC) $(CPPDEFS) $(CPPFLAGS) -eP $*.F90
.F90.lst:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) $(LIST) -c $*.F90
.F90.o:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c     $*.F90
.F90.s:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) -c -eS $*.F90
.F90.x:
	$(FC) $(CPPDEFS) $(CPPFLAGS) $(FFLAGS) $(LDFLAGS) -o $*.x $*.F90
.x.proc:
	procstat -R $*.proc $*.x
.x.hpm:
	hpm -r -o $*.hpm $*.x
"""

        with open(makeinc_path, "w") as makeinc:
            makeinc.write(config[self.compiler.name] + config["post"])

    def build(self, spec, prefix):

        # cd ${ACCESS_OM_DIR}/src/mom/exp
        # export mom_type=ACCESS-OM
        # ./MOM_compile.csh --type $mom_type --platform spack
        with working_dir(join_path(self.stage.source_path, "exp")):
            build = Executable("./MOM_compile.csh")
            build(
                "--type",
                self._mom_type,
                "--platform",
                self._platform,
                "--no_environ"
            )

    def install(self, spec, prefix):

        mkdirp(prefix.bin)
        install(
            join_path(
                "exec",
                self._platform,
                self._mom_type,
                "fms_" + self._mom_type + ".x"
            ),
            prefix.bin
        )
        install(join_path("bin", "mppnccombine." + self._platform), prefix.bin)
