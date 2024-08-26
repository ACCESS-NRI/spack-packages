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
    submodules = True

    maintainers("harshula", "penguian")

    version("master", branch="master", preferred=True)
    version("access-esm1.5", branch="access-esm1.5")
    version("access-esm1.6", branch="master")

    variant("restart_repro", default=True, description="Reproducible restart build.")
    # The following two variants are not applicable when version is "access-esm1.5":
    variant("deterministic", default=False, description="Deterministic build.")
    variant("optimisation_report", default=False, description="Generate optimisation reports.")
    variant("type", default="ACCESS-OM",
        values=("ACCESS-CM", "ACCESS-ESM", "ACCESS-OM", "ACCESS-OM-BGC", "MOM_solo"),
        multi=False,
        description="Build MOM5 to support a particular use case.")

    with when("@:access-esm0,access-esm2:"):
        depends_on("netcdf-c@4.7.4:")
        depends_on("netcdf-fortran@4.5.2:")
        # Depend on virtual package "mpi".
        depends_on("mpi")
        depends_on("datetime-fortran")
        depends_on("oasis3-mct+deterministic", when="+deterministic")
        depends_on("oasis3-mct~deterministic", when="~deterministic")
        depends_on("libaccessom2+deterministic", when="+deterministic")
        depends_on("libaccessom2~deterministic", when="~deterministic")
    with when("@access-esm1.5:access-esm1.6"):
        depends_on("netcdf-c@4.7.1:4.7.4")
        depends_on("netcdf-fortran@4.5.1:4.5.2")
        # Depend on "openmpi".
        depends_on("openmpi@4.0.2:4.1.0")
        depends_on("oasis3-mct@access-esm1.5")

    phases = ["edit", "build", "install"]

    _platform = "spack"

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/mom5/tarball/{0}".format(version)

    def edit(self, spec, prefix):

        srcdir = self.stage.source_path
        makeinc_path = join_path(srcdir, "bin", "mkmf.template.spack")
        config = {}

        # NOTE: The order of the libraries matters during the linking step!
        if self.spec.satisfies("@access-esm1.5:access-esm1.6"):
            istr = " ".join([
                    join_path((spec["oasis3-mct"].headers).cpp_flags, "psmile.MPI1"),
                    join_path((spec["oasis3-mct"].headers).cpp_flags, "mct")])
            ideps = ["netcdf-fortran"]
            ldeps = ["oasis3-mct", "netcdf-c", "netcdf-fortran"]
            FFLAGS_OPT = "-O3 -debug minimal -xCORE-AVX512 -align array64byte"
            CFLAGS_OPT = "-O2 -debug minimal -no-vec"
        else:
            istr = join_path((spec["oasis3-mct"].headers).cpp_flags, "psmile.MPI1")
            ideps = ["oasis3-mct", "libaccessom2", "netcdf-fortran"]
            # NOTE: datetime-fortran is a dependency of libaccessom2.
            ldeps = ["oasis3-mct", "libaccessom2", "netcdf-c", "netcdf-fortran", "datetime-fortran"]

            # TODO: https://github.com/ACCESS-NRI/ACCESS-OM/issues/12
            FFLAGS_OPT = "-g3 -O2 -xCORE-AVX2 -debug all -check none -traceback"
            CFLAGS_OPT = "-O2 -debug minimal -xCORE-AVX2"
            if "+deterministic" in self.spec:
                FFLAGS_OPT = "-g0 -O0 -xCORE-AVX2 -debug none -check none"
                CFLAGS_OPT = "-O0 -debug none -xCORE-AVX2"

        incs = " ".join([istr] + [(spec[d].headers).cpp_flags for d in ideps])
        libs = " ".join([(spec[d].libs).ld_flags for d in ldeps])

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
        if self.spec.satisfies("@access-esm1.5:access-esm1.6"):
            config["intel"] = f"""
ifeq ($(VTRACE), yes)
    FC = mpifort-vt
    LD = mpifort-vt
else
    FC = mpifort
    LD = mpifort
endif

CC = mpicc

REPRO =
VERBOSE =
OPT = on

MAKEFLAGS += --jobs=4

INCLUDE = {incs}

FPPFLAGS := -fpp -Wp,-w $(INCLUDE)
FFLAGS := -fno-alias -safe-cray-ptr -fpe0 -ftz -assume byterecl -i4 -r8 -traceback -nowarn -check noarg_temp_created -assume buffered_io -convert big_endian
FFLAGS_OPT = {FFLAGS_OPT}
FFLAGS_DEBUG = -g -O0 -debug all -check -check noarg_temp_created -check nopointer -warn -warn noerrors -ftrapuv
FFLAGS_REPRO = -O2 -debug minimal -no-vec -fp-model precise
FFLAGS_VERBOSE = -v -V -what

CFLAGS := -D__IFC $(INCLUDE)
CFLAGS_OPT = {CFLAGS_OPT}
CFLAGS_DEBUG = -O0 -g -ftrapuv -traceback

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

LIBS := {libs}

LDFLAGS += $(LIBS)
"""
        else:
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
FFLAGS := -fno-alias -safe-cray-ptr -fpe0 -ftz -assume byterecl -i4 -r8 -nowarn -check noarg_temp_created -assume nobuffered_io -convert big_endian -grecord-gcc-switches -align all
FFLAGS_OPT := {FFLAGS_OPT}
FFLAGS_REPORT := -qopt-report=5 -qopt-report-annotate
FFLAGS_DEBUG := -g3 -O0 -debug all -check -check noarg_temp_created -check nopointer -warn -warn noerrors -ftrapuv -traceback
FFLAGS_REPRO := -fp-model precise -fp-model source -align all
FFLAGS_VERBOSE := -v -V -what

CFLAGS := -D__IFC $(INCLUDE)
CFLAGS_OPT := {CFLAGS_OPT}
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

        # Add support for the ifx compiler
        config["oneapi"] = config["intel"]

        if self.spec.satisfies("@access-esm1.5:access-esm1.6"):
            config["post"] = """
# you should never need to change any lines below.

# see the MIPSPro F90 manual for more details on some of the file extensions
# discussed here.
# this makefile template recognizes fortran sourcefiles with extensions
# .f, .f90, .F, .F90. Given a sourcefile <file>.<ext>, where <ext> is one of
# the above, this provides a number of default actions:

# make <file>.opt	create an optimization report
# make <file>.o		create an object file
# make <file>.s		create an assembly listing
# make <file>.x		create an executable file, assuming standalone
#			source
# make <file>.i		create a preprocessed file (for .F)
# make <file>.i90	create a preprocessed file (for .F90)

# The macro TMPFILES is provided to slate files like the above for removal.

RM = rm -f
SHELL = /bin/csh -f
TMPFILES = .*.m *.B *.L *.i *.i90 *.l *.s *.mod *.opt

.SUFFIXES: .F .F90 .H .L .T .f .f90 .h .i .i90 .l .o .s .opt .x

.f.L:
	$(FC) $(FFLAGS) -c -listing $*.f
.f.opt:
	$(FC) $(FFLAGS) -c -opt_report_level max -opt_report_phase all -opt_report_file $*.opt $*.f
.f.l:
	$(FC) $(FFLAGS) -c $(LIST) $*.f
.f.T:
	$(FC) $(FFLAGS) -c -cif $*.f
.f.o:
	$(FC) $(FFLAGS) -c $*.f
.f.s:
	$(FC) $(FFLAGS) -S $*.f
.f.x:
	$(FC) $(FFLAGS) -o $*.x $*.f *.o $(LDFLAGS)
.f90.L:
	$(FC) $(FFLAGS) -c -listing $*.f90
.f90.opt:
	$(FC) $(FFLAGS) -c -opt_report_level max -opt_report_phase all -opt_report_file $*.opt $*.f90
.f90.l:
	$(FC) $(FFLAGS) -c $(LIST) $*.f90
.f90.T:
	$(FC) $(FFLAGS) -c -cif $*.f90
.f90.o:
	$(FC) $(FFLAGS) -c $*.f90
.f90.s:
	$(FC) $(FFLAGS) -c -S $*.f90
.f90.x:
	$(FC) $(FFLAGS) -o $*.x $*.f90 *.o $(LDFLAGS)
.F.L:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -listing $*.F
.F.opt:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -opt_report_level max -opt_report_phase all -opt_report_file $*.opt $*.F
.F.l:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c $(LIST) $*.F
.F.T:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -cif $*.F
.F.f:
	$(FC) $(CPPDEFS) $(FPPFLAGS) -EP $*.F > $*.f
.F.i:
	$(FC) $(CPPDEFS) $(FPPFLAGS) -P $*.F
.F.o:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c $*.F
.F.s:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -S $*.F
.F.x:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -o $*.x $*.F *.o $(LDFLAGS)
.F90.L:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -listing $*.F90
.F90.opt:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -opt_report_level max -opt_report_phase all -opt_report_file $*.opt $*.F90
.F90.l:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c $(LIST) $*.F90
.F90.T:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -cif $*.F90
.F90.f90:
	$(FC) $(CPPDEFS) $(FPPFLAGS) -EP $*.F90 > $*.f90
.F90.i90:
	$(FC) $(CPPDEFS) $(FPPFLAGS) -P $*.F90
.F90.o:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c $*.F90
.F90.s:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -c -S $*.F90
.F90.x:
	$(FC) $(CPPDEFS) $(FPPFLAGS) $(FFLAGS) -o $*.x $*.F90 *.o $(LDFLAGS)
"""
        else:
            # Copied from bin/mkmf.template.t90
            # TODO: Why from `mkmf.template.t90`? Copy bin/mkmf.template.nci.
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

        fullconfig = config[self.compiler.name] + config["post"]
        print(fullconfig)
        with open(makeinc_path, "w") as makeinc:
            makeinc.write(fullconfig)

    def build(self, spec, prefix):

        # cd ${ACCESS_OM_DIR}/src/mom/exp
        # export mom_type=ACCESS-OM
        # ./MOM_compile.csh --type $mom_type --platform spack
        with working_dir(join_path(self.stage.source_path, "exp")):
            build = Executable("./MOM_compile.csh")
            if "+restart_repro" in self.spec:
                build.add_default_env("REPRO", "true")
            if not self.spec.satisfies("@access-esm1.5"):
                # The MOM5 commit d7ba13a3f364ce130b6ad0ba813f01832cada7a2
                # requires the --no_version switch to avoid git hashes being
                # embedded in the binary.
                build.add_default_arg("--no_version")
                if "+optimisation_report" in self.spec:
                    build.add_default_env("REPORT", "true")
            build(
                "--type",
                self.spec.variants["type"].value,
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
                self.spec.variants["type"].value,
                "fms_" + self.spec.variants["type"].value + ".x"
            ),
            prefix.bin
        )
        install(join_path("bin", "mppnccombine." + self._platform), prefix.bin)
