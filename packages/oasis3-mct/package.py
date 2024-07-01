# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2022 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import install, join_path, mkdirp
# from pprint import pprint

# https://spack.readthedocs.io/en/latest/build_systems/makefilepackage.html
class Oasis3Mct(MakefilePackage):
    """ACCESS-NRI's fork of https://gitlab.com/cerfacs/oasis3-mct OASIS3-MCT 2.0."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/oasis3-mct.git"

    maintainers("harshula", "penguian")

    version("master", branch="master", preferred=True)
    version("access-esm1.5", branch="access-esm1.5")

    variant("deterministic", default=False, description="Deterministic build.")
    variant("optimisation_report", default=False, description="Generate optimisation reports.")

    with when("@:access-esm0,access-esm2:"):
        depends_on("netcdf-fortran@4.5.2:")
        # Depend on virtual package "mpi".
        depends_on("mpi")
    with when("@access-esm1.5"):
        depends_on("hdf5@1.10.5:1.10.11")
        depends_on("netcdf-fortran@4.5.1:4.5.2")
        # Depend on "openmpi".
        depends_on("openmpi@4.0.2:4.1.0")

    phases = ["edit", "build", "install"]

    # TODO: Implement a determine_version(cls, exe)

    __builddir = "compile_oa3-mct"
    __incdir = join_path(__builddir, "build", "lib")
    __libdir = join_path(__builddir, "lib")
    __pkgdir = join_path(__libdir, "pkgconfig")
    __makefiledir = join_path("util", "make_dir")
    __makeinc = join_path(__makefiledir, "make.inc")
    __libs = {"mct": {}, "mpeu": {}, "psmile.MPI1": {}, "scrip": {}}

    # doc/oasis3mct_UserGuide.pdf:
    # If module mod_oasis is used in the models, it is enough to include
    # the path of the psmile objects and modules
    # ($ARCHDIR/build/lib/psmile.MPI1) for the compilation and to use the
    # psmile library $ARCHDIR/lib/libpsmile.MPI1.a when linking.
    # If module mod_prism is used in the models, it is necessary to include
    # the path of the psmile and of the mct objects and modules for the
    # compilation (i.e. $ARCHDIR/build/lib/psmile.MPI1 and /mct and to
    # use both the psmile and mct libraries $ARCHDIR/lib/libpsmile.MPI1.a
    # and libmct.a and libmpeu.a when linking.

    __libs["mct"]["incfiles"] = [
        "m_accumulatorcomms.mod",
        "m_accumulator.mod",
        "m_attrvectcomms.mod",
        "m_attrvect.mod",
        "m_attrvectreduce.mod",
        "m_chars.mod",
        "m_convertmaps.mod",
        "mct_mod.mod",
        "m_die.mod",
        "m_dropdead.mod",
        "m_errorhandler.mod",
        "m_exchangemaps.mod",
        "m_fccomms.mod",
        "m_filename.mod",
        "m_fileresolv.mod",
        "m_flow.mod",
        "m_generalgridcomms.mod",
        "m_generalgrid.mod",
        "m_globalmap.mod",
        "m_globalsegmapcomms.mod",
        "m_globalsegmap.mod",
        "m_globaltolocal.mod",
        "m_indexbin_char.mod",
        "m_indexbin_integer.mod",
        "m_indexbin_logical.mod",
        "m_inpak90.mod",
        "m_ioutil.mod",
        "m_list.mod",
        "m_mall.mod",
        "m_matattrvectmul.mod",
        "m_mctworld.mod",
        "m_merge.mod",
        "m_mergesorts.mod",
        "m_mpif90.mod",
        "m_mpif.mod",
        "m_mpout.mod",
        "m_navigator.mod",
        "m_permuter.mod",
        "m_rankmerge.mod",
        "m_realkinds.mod",
        "m_rearranger.mod",
        "m_router.mod",
        "m_sortingtools.mod",
        "m_sparsematrixcomms.mod",
        "m_sparsematrixdecomp.mod",
        "m_sparsematrix.mod",
        "m_sparsematrixplus.mod",
        "m_sparsematrixtomaps.mod",
        "m_spatialintegral.mod",
        "m_spatialintegralv.mod",
        "m_stdio.mod",
        "m_string.mod",
        "m_strtemplate.mod",
        "m_traceback.mod",
        "m_transfer.mod",
        "m_zeit.mod",
    ]

    __libs["mpeu"]["incfiles"] = []

    __libs["psmile.MPI1"]["incfiles"] = [
        "mod_oasis_advance.mod",
        "mod_oasis_coupler.mod",
        "mod_oasis_data.mod",
        "mod_oasis_getput_interface.mod",
        "mod_oasis_grid.mod",
        "mod_oasis_io.mod",
        "mod_oasis_ioshr.mod",
        "mod_oasis_kinds.mod",
        "mod_oasis_method.mod",
        "mod_oasis.mod",
        "mod_oasis_mpi.mod",
        "mod_oasis_namcouple.mod",
        "mod_oasis_parameters.mod",
        "mod_oasis_part.mod",
        "mod_oasis_string.mod",
        "mod_oasis_sys.mod",
        "mod_oasis_timer.mod",
        "mod_oasis_var.mod",
        "mod_prism.mod",
    ]

    __libs["scrip"]["incfiles"] = [
        "constants.mod",
        "grids.mod",
        "iounits.mod",
        "kinds_mod.mod",
        "mod_oasis_flush.mod",
        "netcdf_mod.mod",
        "remap_bicubic.mod",
        "remap_bicubic_reduced.mod",
        "remap_bilinear.mod",
        "remap_bilinear_reduced.mod",
        "remap_conservative.mod",
        "remap_distance_weight.mod",
        "remap_gaussian_weight.mod",
        "remap_vars.mod",
        "remap_write.mod",
        "timers.mod",
    ]

    def __init__(self, args):
        super().__init__(args)

        for k in self.__libs.keys():
            self.__libs[k]["filename"] = "lib" + k + ".a"
            self.__libs[k]["filerelpath"] = join_path(
                "lib", self.__libs[k]["filename"]
            )
            self.__libs[k]["pcname"] = "oasis3-" + k + ".pc"
            self.__libs[k]["pcrelpath"] = join_path(
                "lib", "pkgconfig", self.__libs[k]["pcname"]
            )
            self.__libs[k]["pcpath"] = join_path(
                self.__pkgdir, self.__libs[k]["pcname"]
            )

        # Uncomment to print package files and directories
        # pprint(self.__libs)

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/oasis3-mct/tarball/{0}".format(version)

    def __create_pkgconfig(self, spec, prefix):

        mkdirp(self.__pkgdir)
        for k in self.__libs.keys():
            text = f"""\
prefix={prefix}
exec_prefix=${{prefix}}
libdir=${{exec_prefix}}/lib
includedir=${{prefix}}/include

Name: {k}
Description: OASIS3-MCT 2.0 {k} Library for Fortran
Version: 2.0
Libs: -L${{libdir}} -l{k}
Cflags: -I${{includedir}}/{k}
"""

            with open(self.__libs[k]["pcpath"], "w", encoding="utf-8") as pc:
                nchars_written = pc.write(text)

            if nchars_written < len(text):
                raise OSError

    # https://spack-tutorial.readthedocs.io/en/ecp21/tutorial_advanced_packaging.html
    @property
    def libs(self):
        # NOTE: The order matters during the linking step of the cice5 build!
        # "-lpsmile.MPI1 -lmct -lmpeu -lscrip"
        libraries = ["libpsmile.MPI1", "libmct", "libmpeu", "libscrip"]
        return find_libraries(
            libraries, root=self.prefix, shared=False, recursive=True
        )

    # Following pattern:
    # https://spack-tutorial.readthedocs.io/en/latest/tutorial_buildsystems.html
    def edit(self, spec, prefix):
        SRCDIR = self.stage.source_path
        makeinc_path = join_path(SRCDIR, self.__makeinc)
        config = {}

        # TODO: https://github.com/ACCESS-NRI/ACCESS-OM/issues/12
        NCI_OPTIM_FLAGS = "-g3 -O2 -axCORE-AVX2 -debug all -check none -traceback"
        CFLAGS = ""
        if "@access-esm1.5" in self.spec:
            NCI_OPTIM_FLAGS = "-g3 -O2 -xCORE-AVX512 -debug all -check none -traceback"
            
        if "+deterministic" in self.spec:
            NCI_OPTIM_FLAGS = "-g0 -O0 -axCORE-AVX2 -debug none -check none"
            CFLAGS = "-g0"

        if "+optimisation_report" in self.spec:
            NCI_OPTIM_FLAGS += " -qopt-report=5 -qopt-report-annotate"

        config["pre"] = f"""
# CHAN	: communication technique used in OASIS3 (MPI1/MPI2/NONE)
CHAN            = MPI1
#
# Paths for libraries, object files and binaries
#
# COUPLE	: path for oasis3-mct main directory
COUPLE={SRCDIR}
# ARCHDIR       : directory created when compiling
ARCHDIR= $(COUPLE)/compile_oa3-mct
AR          = ar
ARFLAGS     = -rvD
CFLAGS      = {CFLAGS}
F           = $(F90)
f90         = $(F90)
f           = $(F90)
"""

        config["gcc"] = f"""
# Compiling and other commands
MAKE        = make
F90         = mpif90 -Wall -fallow-argument-mismatch
CC          = gcc
LD          = mpif90
MCT_FCFLAGS =
#
# CPP keys and compiler options
# 
CPPDEF    = -Duse_netCDF -Duse_comm_$(CHAN) -D__VERBOSE -DTREAT_OVERLAY
F90FLAGS_1  = 
"""

        # module load intel-compiler/2019.5.281
        config["intel"] = f"""
# Compiling and other commands
MAKE        = /usr/bin/make
F90         = mpifort
CC          = mpicc
LD          = $(F90)

# -g is necessary in F90FLAGS and LDFLAGS for pgf90 versions lower than 6.1
# For compiling in double precision, put -r8
# For compiling in single precision, remove -r8 and add -Duse_realtype_single
# Causes non-deterministic builds: -traceback -debug all
NCI_INTEL_FLAGS = -r8 -i4 -fpe0 -convert big_endian -fno-alias -ip -check noarg_temp_created
NCI_REPRO_FLAGS = -fp-model precise -fp-model source -align all
ifeq ($(DEBUG), yes)
    NCI_DEBUG_FLAGS = -g3 -O0 -fpe0 -no-vec -debug all -check all -no-vec -traceback
    F90FLAGS_1      = $(NCI_INTEL_FLAGS) $(NCI_REPRO_FLAGS) $(NCI_DEBUG_FLAGS)
    CPPDEF          = -Duse_netCDF -Duse_comm_$(CHAN) -DTREAT_OVERLAY -DDEBUG -D__VERBOSE
    MCT_FCFLAGS     = $(NCI_REPRO_FLAGS) $(NCI_DEBUG_FLAGS) -ip
else
    NCI_OPTIM_FLAGS = {NCI_OPTIM_FLAGS}
    F90FLAGS_1      = $(NCI_INTEL_FLAGS) $(NCI_REPRO_FLAGS) $(NCI_OPTIM_FLAGS)
    CPPDEF          = -Duse_netCDF -Duse_comm_$(CHAN) -DTREAT_OVERLAY
    MCT_FCFLAGS     = $(NCI_REPRO_FLAGS) $(NCI_OPTIM_FLAGS) -ip
endif
"""

        # Add support for the ifx compiler
        config["oneapi"] = config["intel"]

        config["post"] = f"""
f90FLAGS_1  = $(F90FLAGS_1)
FFLAGS_1    = $(F90FLAGS_1)
fFLAGS_1    = $(F90FLAGS_1)
CCFLAGS_1   = 
LDFLAGS     = 
#
###################
#
# Additional definitions that should not be changed
#
FLIBS		= ""
# BINDIR        : directory for executables
BINDIR          = $(ARCHDIR)/bin
# LIBBUILD      : contains a directory for each library
LIBBUILD        = $(ARCHDIR)/build/lib
# INCPSMILE     : includes all *o and *mod for each library
INCPSMILE       = -I$(LIBBUILD)/psmile.$(CHAN) -I$(LIBBUILD)/mct 

F90FLAGS  = $(F90FLAGS_1) $(INCPSMILE) $(CPPDEF)
f90FLAGS  = $(f90FLAGS_1) $(INCPSMILE) $(CPPDEF)
FFLAGS    = $(FFLAGS_1) $(INCPSMILE) $(CPPDEF)
fFLAGS    = $(fFLAGS_1) $(INCPSMILE) $(CPPDEF)
CCFLAGS   = $(CCFLAGS_1) $(INCPSMILE) $(CPPDEF)
#
#############################################################################
"""

        with open(makeinc_path, "w") as makeinc:
            makeinc.write(
                config["pre"]
                + config[self.compiler.name]
                + config["post"]
            )

    def build(self, spec, prefix):
        # See doc/oasis3mct_UserGuide.pdf:
        #
        # compiles all OASIS3-MCT libraries mct, scrip and psmile:
        # make -f TopMakefileOasis3
        with working_dir(join_path(self.stage.source_path, self.__makefiledir)):
            build = Executable("make")
            build("-f", "TopMakefileOasis3")

        # Upstream is missing a pkgconfig files, so we'll create them.
        self.__create_pkgconfig(spec, prefix)

    def install(self, spec, prefix):

        mkdirp(prefix.lib.pkgconfig)

        src_dst = []
        for libname in self.__libs.keys():

            mkdirp(join_path(prefix.include, libname))

            for f in [
                self.__libs[libname]["filerelpath"],
                self.__libs[libname]["pcrelpath"],
            ]:
                src_dst.append(
                    (join_path(self.__builddir, f), join_path(prefix, f))
                )

            for f in self.__libs[libname]["incfiles"]:
                src_dst.append(
                    (
                        join_path(self.__incdir, libname, f),
                        join_path(prefix.include, libname, f),
                    )
                )

        # Uncomment to print source and destination tuples
        # pprint(src_dst)
        [install(s, d) for (s, d) in src_dst]
