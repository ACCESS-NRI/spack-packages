# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2022 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import install, join_path, mkdirp
from pprint import pprint
from itertools import repeat

class Oasis3Mct(Package):
    """ACCESS-NRI's fork of https://gitlab.com/cerfacs/oasis3-mct OASIS3-MCT 2.0."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/oasis3-mct.git"

    maintainers = ["harshula"]

    version("5e57b1aa40840adb6d6747d475dabadab5d9d6fb", commit="5e57b1aa40840adb6d6747d475dabadab5d9d6fb")

    depends_on("netcdf-fortran@4.5.2:")
    depends_on("openmpi@4.0.2:")

    phases = ["build", "install"]

    def build(self, spec, prefix):
        # TODO: Need to rethink the build process. Likely require modifying
        #       oasis3-mct
        build = Executable("./build.sh")
        build()

    def install(self, spec, prefix):

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

        libs = ["libmct.a", "libmpeu.a", "libpsmile.MPI1.a", "libscrip.a"]

        incsrcdir = join_path("compile_oa3-mct", "build", "lib")
        libsrcdir = join_path("compile_oa3-mct", "lib")

        incdstdir = self.prefix.include
        mkdirp(join_path(incdstdir, "mct"))
        mkdirp(join_path(incdstdir, "psmile.MPI1"))
        mkdirp(join_path(incdstdir, "scrip"))

        libdstdir = self.prefix.lib
        mkdirp(libdstdir)

        inc_list_of_tuples = [(join_path(incsrcdir, f), join_path(incdstdir, f)) for f in incs]
        lib_list_of_tuples = [(join_path(libsrcdir, f), join_path(libdstdir, f)) for f in libs]

        [install(s,d) for (s,d) in inc_list_of_tuples + lib_list_of_tuples]

