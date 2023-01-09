# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2022 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import install, join_path, mkdirp
from pprint import pprint
import os
import inspect

# https://spack.readthedocs.io/en/latest/build_systems/makefilepackage.html
class Oasis3Mct(MakefilePackage):
    """ACCESS-NRI's fork of https://gitlab.com/cerfacs/oasis3-mct OASIS3-MCT 2.0."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/oasis3-mct.git"
    # NOTE: URL definition required for CI
    # Spack needs tarball URL to be defined to access github branches
    url = "https://github.com/ACCESS-NRI/oasis3-mct/tarball/spack-build"

    maintainers = ["harshula"]

    version("spack-build", branch="spack-build")

    depends_on("netcdf-fortran@4.5.2:")
    # TODO: Should we depend on virtual package "mpi" instead?
    depends_on("openmpi@4.0.2:")

    phases = ["build", "install"]

    # TODO: Implement a determine_version(cls, exe)

    __builddir = "compile_oa3-mct"
    __incdir = join_path(__builddir, "build", "lib")
    __libdir = join_path(__builddir, "lib")
    __pkgdir = join_path(__libdir, "pkgconfig")
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

    __libs["mct"]["incfiles"] = [ "m_accumulatorcomms.mod",
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
                                  "m_zeit.mod" ]

    __libs["mpeu"]["incfiles"] = []

    __libs["psmile.MPI1"]["incfiles"] = [ "mod_oasis_advance.mod",
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
                                          "mod_prism.mod" ]

    __libs["scrip"]["incfiles"] = [ "constants.mod",
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
                                    "timers.mod" ]

    def __init__(self, args):
        super().__init__(args)

        for k in self.__libs.keys():
            self.__libs[k]["filename"] = "lib" + k + ".a"
            self.__libs[k]["filerelpath"] = join_path("lib", self.__libs[k]["filename"])
            self.__libs[k]["pcname"] = "oasis3-" + k + ".pc"
            self.__libs[k]["pcrelpath"] = join_path("lib", "pkgconfig", self.__libs[k]["pcname"])
            self.__libs[k]["pcpath"] = join_path(self.__pkgdir, self.__libs[k]["pcname"])

        # Uncomment to print package files and directories
        # pprint(self.__libs)


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



    def build(self, spec, prefix):
        # See doc/oasis3mct_UserGuide.pdf:
        #
        # compiles all OASIS3-MCT libraries mct, scrip and psmile:
        # make -f TopMakefileOasis3
        srcdir = os.getcwd()
        print(f"cwd: {srcdir}")
        makefile_dir = join_path(srcdir, "util", "make_dir")
        with working_dir(makefile_dir):
            with open("make.inc", 'w') as makeinc:
                makespack = join_path(makefile_dir, "make.spack")
                makeinc.write(f"include {makespack}")

            build = Executable("make")
            build.add_default_env("OASIS_HOME", srcdir)
            build("-f", "TopMakefileOasis3", "F90=mpif90", "CC=gcc")

        # Upstream is missing a pkgconfig files, so we'll create them.
        self.__create_pkgconfig(spec, prefix)


    def install(self, spec, prefix):

        mkdirp(prefix.lib.pkgconfig)

        src_dst = []
        for libname in self.__libs.keys():

            mkdirp(join_path(prefix.include, libname))

            for f in [ self.__libs[libname]["filerelpath"],
                       self.__libs[libname]["pcrelpath"] ]:
                src_dst.append( (join_path(self.__builddir, f),
                                 join_path(prefix, f)) )

            for f in self.__libs[libname]["incfiles"]:
                src_dst.append( (join_path(self.__incdir, libname, f),
                                 join_path(prefix.include, libname, f)) )

        # Uncomment to print source and destination tuples
        # pprint(src_dst)
        [install(s,d) for (s,d) in src_dst]

