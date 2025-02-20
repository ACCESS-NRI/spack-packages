# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import install, join_path, mkdirp

# https://spack.readthedocs.io/en/latest/build_systems/makefilepackage.html
class Cice5(MakefilePackage):
    """The Los Alamos sea ice model (CICE) is the result of an effort to develop a computationally efficient sea ice component for a fully coupled atmosphere-land global climate model."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/cice5.git"

    maintainers("harshula", "anton-seaice")

    version("access-om2", branch="master", preferred=True)
    version("access-esm1.6", branch="access-esm1.6")

    variant("deterministic", default=False, description="Deterministic build.")
    variant("optimisation_report", default=False, description="Generate optimisation reports.")

    # Depend on virtual package "mpi".
    depends_on("mpi")
    depends_on("netcdf-fortran@4.5.2:")
    depends_on("netcdf-c@4.7.4:")
    depends_on("datetime-fortran")
    depends_on("oasis3-mct+deterministic", when="+deterministic")
    depends_on("oasis3-mct~deterministic", when="~deterministic")

    # These are the default dependencies when building version "master".
    # Copied with when() from MOM5 SPR
    with when("@:access-esm0,access-esm2:"):
        # TODO: For initial verification we are going to use static pio.
        #       Eventually we plan to move to shared pio
        # ~shared requires: https://github.com/spack/spack/pull/34837
        depends_on("parallelio~pnetcdf~timing~shared")
        depends_on("libaccessom2+deterministic", when="+deterministic")
        depends_on("libaccessom2~deterministic", when="~deterministic")

    phases = ["set_deps_targets", "edit", "build", "install"]

    __buildscript = "spack-build.sh"
    __buildscript_path = join_path("bld", __buildscript)

    __deps = {"includes": "", "ldflags": ""}
    __targets = {}

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/cice5/tarball/{0}".format(version)

    # The reason for the explicit -rpath is:
    # https://github.com/ACCESS-NRI/spack-packages/issues/14#issuecomment-1653651447
    def get_linker_args(self, spec, name):
        return " ".join(
                    [(spec[name].libs).ld_flags,
                    "-Wl,-rpath=" + join_path(spec[name].prefix, "lib")]
                   )

    # The reason for the explicit -rpath is:
    # https://github.com/ACCESS-NRI/spack-packages/issues/14#issuecomment-1653651447
    def make_linker_args(self, spec, name, namespecs):
        path = join_path(spec[name].prefix, "lib")
        return " ".join(
                    ["-L" + path,
                    namespecs,
                    "-Wl,-rpath=" + path]
                   )

    def add_target(self, ntask, driver, grid, blocks):
        self.__targets[ntask]["driver"] = driver
        self.__targets[ntask]["grid"] = grid
        self.__targets[ntask]["blocks"] = blocks

    def set_deps_targets(self, spec, prefix):

        if self.spec.satisfies("@access-esm1.6"):
            # The integer represents environment variable NTASK
            # esm1.5 used 12 (cice4), cm2 used 16 (cice5), build both for testing
            self.__targets = {12: {}, 16: {}} 
            self.add_target(12, "access-esm1.6", "360x300", "12x1")
            self.add_target(16, "access-esm1.6", "360x300", "8x2")

            ideps = ["oasis3-mct", "netcdf-fortran"]

            # NOTE: The order of the libraries matter during the linking step!
            ldeps = ["oasis3-mct", "netcdf-c", "netcdf-fortran"]
            lstr = ""

        # These are the default settings when building version "master".
        else:
            # The integer represents environment variable NTASK
            self.__targets = {24: {}, 480: {}, 722: {}, 1682: {}}

            # TODO: Each of these targets could map to a variant:
            self.add_target(24, "auscom", "360x300", "24x1")
            self.add_target(480, "auscom", "1440x1080", "48x40")

            # Comment from bld/config.nci.auscom.3600x2700:
            # Recommendations:
            #   use processor_shape = slenderX1 or slenderX2 in ice_in
            #   one per processor with distribution_type='cartesian' or
            #   squarish blocks with distribution_type='rake'
            # If BLCKX (BLCKY) does not divide NXGLOB (NYGLOB) evenly, padding
            # will be used on the right (top) of the grid.
            self.add_target(722, "auscom", "3600x2700", "90x90")
            self.add_target(1682, "auscom", "3600x2700", "200x180")

            ideps = ["parallelio", "oasis3-mct", "libaccessom2", "netcdf-fortran"]

            # NOTE: The order of the libraries matter during the linking step!
            # NOTE: datetime-fortran is a dependency of libaccessom2.
            ldeps = ["oasis3-mct", "libaccessom2", "netcdf-c", "netcdf-fortran", "datetime-fortran"]
            lstr = self.make_linker_args(spec, "parallelio", "-lpiof -lpioc")

        istr = join_path((spec["oasis3-mct"].headers).cpp_flags, "psmile.MPI1")
        self.__deps["includes"] = " ".join([istr] + [(spec[d].headers).cpp_flags for d in ideps])

        self.__deps["ldflags"] = " ".join([lstr] + [self.get_linker_args(spec, d) for d in ldeps])


    def edit(self, spec, prefix):

        srcdir = self.stage.source_path
        buildscript_dest = join_path(srcdir, self.__buildscript_path)
        makeinc_path = join_path(srcdir, "bld", "Macros.spack")

        copy(join_path(self.package_dir, self.__buildscript), buildscript_dest)

        config = {}
        incs = self.__deps["includes"]
        libs = self.__deps["ldflags"]

        # TODO: https://github.com/ACCESS-NRI/ACCESS-OM/issues/12
        NCI_OPTIM_FLAGS = "-g3 -O2 -axCORE-AVX2 -debug all -check none -traceback -assume buffered_io"
        CFLAGS = "-c -O2"
        if "+deterministic" in self.spec:
            NCI_OPTIM_FLAGS = "-g0 -O0 -axCORE-AVX2 -debug none -check none -assume buffered_io"
            CFLAGS = "-c -g0"

        if "+optimisation_report" in self.spec:
            NCI_OPTIM_FLAGS += " -qopt-report=5 -qopt-report-annotate"

        # Copied from bld/Macros.nci
        config["pre"] = f"""
INCLDIR    := -I. {incs}
SLIBS      := {libs}
ULIBS      :=
CPP        := cpp
FC         := mpifort

CPPFLAGS   := -P -traditional
CPPDEFS    := -DLINUX -DPAROPT
CFLAGS     := {CFLAGS}
FIXEDFLAGS := -132
FREEFLAGS  :=
"""

        config["gcc"] = f"""
# TODO: removed -std=f2008 due to compiler errors
FFLAGS = -Wall -fdefault-real-8 -fdefault-double-8 -ffpe-trap=invalid,zero,overflow -fallow-argument-mismatch
"""

        # module load intel-compiler/2019.5.281
        config["intel"] = f"""
NCI_INTEL_FLAGS := -r8 -i4 -w -fpe0 -ftz -convert big_endian -assume byterecl -check noarg_temp_created
NCI_REPRO_FLAGS := -fp-model precise -fp-model source -align all
ifeq ($(DEBUG), 1)
    NCI_DEBUG_FLAGS := -g3 -O0 -debug all -check all -no-vec -traceback -assume nobuffered_io
    FFLAGS          := $(NCI_INTEL_FLAGS) $(NCI_REPRO_FLAGS) $(NCI_DEBUG_FLAGS)
    CPPDEFS         := $(CPPDEFS) -DDEBUG=$(DEBUG)
else
    NCI_OPTIM_FLAGS = {NCI_OPTIM_FLAGS}
    FFLAGS          := $(NCI_INTEL_FLAGS) $(NCI_REPRO_FLAGS) $(NCI_OPTIM_FLAGS)
endif
"""

        # Add support for the ifx compiler
        config["oneapi"] = config["intel"]

        # Copied from bld/Macros.nci
        config["post"] = """
MOD_SUFFIX := mod
LD         := $(FC)
LDFLAGS    := $(FFLAGS) -v

CPPDEFS :=  $(CPPDEFS) -DNXGLOB=$(NXGLOB) -DNYGLOB=$(NYGLOB) \
            -DNUMIN=$(NUMIN) -DNUMAX=$(NUMAX) \
            -DTRAGE=$(TRAGE) -DTRFY=$(TRFY) -DTRLVL=$(TRLVL) \
            -DTRPND=$(TRPND) -DNTRAERO=$(NTRAERO) -DTRBRI=$(TRBRI) \
            -DNBGCLYR=$(NBGCLYR) -DTRBGCS=$(TRBGCS) \
            -DNICECAT=$(NICECAT) -DNICELYR=$(NICELYR) \
            -DNSNWLYR=$(NSNWLYR) \
            -DBLCKX=$(BLCKX) -DBLCKY=$(BLCKY) -DMXBLCKS=$(MXBLCKS)

ifeq ($(COMMDIR), mpi)
   SLIBS   :=  $(SLIBS) -lmpi
endif

ifeq ($(DITTO), yes)
   CPPDEFS :=  $(CPPDEFS) -DREPRODUCIBLE
endif
ifeq ($(BARRIERS), yes)
   CPPDEFS :=  $(CPPDEFS) -Dgather_scatter_barrier
endif

ifeq ($(IO_TYPE), netcdf)
   CPPDEFS :=  $(CPPDEFS) -Dncdf
endif

ifeq ($(IO_TYPE), pio)
   CPPDEFS :=  $(CPPDEFS) -Dncdf -DPIO
endif

# TODO: Do we want to delete this conditional?
#ifeq ($(USE_ESMF), yes)
#   CPPDEFS :=  $(CPPDEFS) -Duse_esmf
#   INCLDIR :=  $(INCLDIR) -I ???
#   SLIBS   :=  $(SLIBS) -L ??? -lesmf -lcprts -lrt -ldl
#endif

ifeq ($(AusCOM), yes)
   CPPDEFS := $(CPPDEFS) -DAusCOM -Dcoupled
endif

ifeq ($(UNIT_TESTING), yes)
   CPPDEFS := $(CPPDEFS) -DUNIT_TESTING
endif
ifeq ($(ACCESS), yes)
   CPPDEFS := $(CPPDEFS) -DACCESS
endif
# standalone CICE with AusCOM mods
ifeq ($(ACCICE), yes)
   CPPDEFS := $(CPPDEFS) -DACCICE
endif
# no MOM just CICE+UM
ifeq ($(NOMOM), yes)
   CPPDEFS := $(CPPDEFS) -DNOMOM
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
                    join_path(self.stage.source_path, self.__buildscript_path)
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
