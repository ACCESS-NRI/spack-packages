# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py
# and https://github.com/coecms/access-esm-build-gadi
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.package import *

import os
import os.path

class Um7(Package):
    """
    UM is a numerical weather prediction and climate modelling software package.
    Um7 is a package for UM vn7.3 for ACCESS ESM 1.5
    """

    homepage = "https://code.metoffice.gov.uk/trac/um"
    git = "git@github.com:ACCESS-NRI/UM_v7.git"

    # https://code.metoffice.gov.uk/trac/um/wiki/PastReleases
    version("7.3")

    maintainers("penguian")

    depends_on("dummygrib", type=("build", "link"))
    depends_on("fcm", type="build")
    depends_on("gcom4+mpi", type=("build", "link"))
    depends_on("mpi", type=("build", "run"))
    depends_on("netcdf-fortran", type=("build", "link"))
    depends_on("oasis3-mct@git.access-esm1.5-new-modules", type=("build", "link"))

    variant("omp", default=True, description="Use OpenMP")
    variant("netcdf", default=True, description="NetCDF")
    variant("opt", default="high", description="Optimization level",
            values=("high", "debug"), multi=False)


    def setup_build_environment(self, env):
        env.prepend_path("PATH", self.spec["fcm"].prefix.bin)
        env.prepend_path("CPATH", self.spec["gcom4"].prefix.include)
        env.prepend_path("CPATH", self.spec["netcdf-c"].prefix.include)
        env.prepend_path("CPATH", self.spec["netcdf-fortran"].prefix.include)
        env.prepend_path("CPATH", self.spec["oasis3-mct"].prefix.include)
        oasis3_mct_includes = []
        for header in self.spec["oasis3-mct"].headers:
            include = os.path.dirname(header)
            if include not in oasis3_mct_includes:
                oasis3_mct_includes.append(include)
                env.prepend_path("CPATH", include)
        env.prepend_path("LIBRARY_PATH", self.spec["dummygrib"].prefix.lib)
        env.prepend_path("LIBRARY_PATH", self.spec["gcom4"].prefix.lib)
        env.prepend_path("LIBRARY_PATH", self.spec["netcdf-c"].prefix.lib)
        env.prepend_path("LIBRARY_PATH", self.spec["netcdf-fortran"].prefix.lib)
        env.prepend_path("LIBRARY_PATH", self.spec["oasis3-mct"].prefix.lib)


    def setup_run_environment(self, env):
        env.prepend_path("LD_LIBRARY_PATH", self.spec["netcdf-c"].prefix.lib)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["netcdf-fortran"].prefix.lib)


    def install(self, spec, prefix):

        boolstr = lambda b: "true" if b else "false"

        fcm = which("fcm")

        if self.compiler.name == "intel":
            env["platform_config_dir"] = "nci-x86-ifort"
        else:
            raise NotImplentedError("Unknown compiler")

        opt_value = spec.variants["opt"].value
        env["optimisation_level"] = opt_value

        env["openmp"] = boolstr("~omp" in spec)
        env["netcdf"] = boolstr("~netcdf" in spec)

        hg = 3  # build HadGEM3 ONLY here

        # Whether to build debug --jhan: adjust path to configs
        if opt_value == "debug":
            bld_config = f"bld-dbg-hadgem{hg}-C2.cfg"
            um_exe = f"um_hg{hg}_dbg.exe"
        else:
            bld_config = f"bld-hadgem{hg}-mct.cfg"
            um_exe = f"um_hg{hg}.exe"

        bld_dir = f"ummodel_hg{hg}"
        # Build with fcm
        fcm("build", "-f", "-j", "4",
            join_path(bld_dir, "cfg", bld_config))

        # Install
        mkdirp(prefix.bin)
        install(
            join_path(bld_dir, "bin", um_exe),
            join_path(prefix.bin, um_exe))

