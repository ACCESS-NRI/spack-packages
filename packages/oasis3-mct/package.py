# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2022 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import install, join_path, mkdirp
from pprint import pprint
import inspect

class Oasis3Mct(Package):
    """ACCESS-NRI's fork of https://gitlab.com/cerfacs/oasis3-mct OASIS3-MCT 2.0."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/oasis3-mct.git"

    maintainers = ["harshula"]

    version("5e57b1aa40840adb6d6747d475dabadab5d9d6fb", commit="5e57b1aa40840adb6d6747d475dabadab5d9d6fb")

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


    def __create_pkgconfig(self, spec, prefix):

        mkdirp(self.__pkgdir)

        for k in self.__libs.keys():
            self.__libs[k]["filename"] = "lib" + k + ".a"
            self.__libs[k]["pcname"] = k + ".pc"
            self.__libs[k]["pcrelpath"] = join_path("pkgconfig", self.__libs[k]["pcname"])
            self.__libs[k]["pcpath"] = join_path(self.__pkgdir, self.__libs[k]["pcname"])
            self.__libs[k]["pctext"] = f"""\
prefix={prefix}
exec_prefix=${{prefix}}
libdir=${{exec_prefix}}/lib
includedir=${{prefix}}/include

Name: {k}
Description: OASIS3-MCT 2.0 {k} Library for Fortran
Version: 2.0
Libs: -L${{libdir}} -l{k}
Cflags: -I${{includedir}}
"""
            text = self.__libs[k]["pctext"]

            with open(self.__libs[k]["pcpath"], "w", encoding="utf-8") as pc:
                nchars_written = pc.write(text)

            if nchars_written < len(text):
                raise OSError

        #pprint(self.__libs)


    def build(self, spec, prefix):
        # TODO: Need to rethink the build process. Likely require modifying
        #       oasis3-mct
        build = Executable("./build.sh")
        build()

        # Upstream is missing a pkgconfig files, so we'll create them.
        self.__create_pkgconfig(spec, prefix)


    def install(self, spec, prefix):

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

        incs_mct = ["m_accumulatorcomms.mod",
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

        incs_psmile = ["mod_oasis_advance.mod",
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
                         "mod_prism.mod"]

        incs_scrip = [ "constants.mod",
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


        incs = [join_path("mct", f) for f in incs_mct] \
                + [join_path("psmile.MPI1", f) for f in incs_psmile] \
                + [join_path("scrip", f) for f in incs_scrip]

        libs = [self.__libs[k]["filename"] for k in self.__libs.keys()] \
                + [self.__libs[k]["pcrelpath"] for k in self.__libs.keys()]

        incdstdir = prefix.include
        mkdirp(prefix.include.mct)
        # The directory name has a '.', so create the path manually:
        mkdirp(join_path(incdstdir, "psmile.MPI1"))
        mkdirp(prefix.include.scrip)

        libdstdir = prefix.lib
        mkdirp(libdstdir)
        mkdirp(prefix.lib.pkgconfig)

        inc_list_of_tuples = [(join_path(self.__incdir, f), join_path(incdstdir, f)) for f in incs]
        lib_list_of_tuples = [(join_path(self.__libdir, f), join_path(libdstdir, f)) for f in libs]

        [install(s,d) for (s,d) in inc_list_of_tuples + lib_list_of_tuples]

