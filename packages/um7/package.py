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
import llnl.util.tty as tty

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

    depends_on("fcm", type="build")
    depends_on("gcom4+mpi", type=("build","link"))
    depends_on("mpi", type=("build","run"))
    depends_on("netcdf-fortran", type=("build","link"))
    depends_on("oasis3-mct", type=("build","link"))


    variant("platform", default="intel", description="Compiler",
            values=("oneapi","intel"), multi=False)
    variant("omp",default=True,description="Use OpenMP")
    variant("netcdf",default=True,description="NetCDF")
    variant("opt",default="high",description="Optimization level",
            values=("high","debug"), multi=False)


    def setup_build_environment(self, env):
        env.prepend_path("PATH", self.spec["fcm"].prefix.bin)
        env.prepend_path("CPATH", self.spec["gcom4"].prefix.include)
        env.prepend_path("CPATH", self.spec["netcdf-c"].prefix.include)
        env.prepend_path("CPATH", self.spec["netcdf-fortran"].prefix.include)
        env.prepend_path("CPATH", self.spec["oasis3-mct"].prefix.include)
        oasis3_mct_includes = []
        for header in self.spec["oasis3-mct"].headers:
            include = os.path.dirname(header)
            if not include in oasis3_mct_includes:
                oasis3_mct_includes.append(include)
                env.prepend_path("CPATH", include)
        env.prepend_path("LIBRARY_PATH", self.spec["gcom4"].prefix.lib)
        env.prepend_path("LIBRARY_PATH", self.spec["netcdf-c"].prefix.lib)
        env.prepend_path("LIBRARY_PATH", self.spec["netcdf-fortran"].prefix.lib)
        env.prepend_path("LIBRARY_PATH", self.spec["oasis3-mct"].prefix.lib)

        '''
        env.set("config_root_path","./")
        env.set("config_type","atmos")
        env.set("fcflags_overrides","")
        env.set("gwd_ussp_precision","double")
        env.set("land_surface_model","jules")
        env.set("ldflags_overrides_prefix","")
        env.set("ldflags_overrides_suffix","")
        env.set("ls_precipitation_precision","double")
        env.set("mirror","mirror")
        env.set("mpp_version","1C")
        env.set("platagnostic","false")
        env.set("portio_version","2A")
        env.set("stash_version","1A")
        env.set("timer_version","3A")
        '''

    def setup_run_environment(self, env):
        env.prepend_path("LD_LIBRARY_PATH", self.spec["netcdf-c"].prefix.lib)
        env.prepend_path("LD_LIBRARY_PATH", self.spec["netcdf-fortran"].prefix.lib)


    def install(self, spec, prefix):

        fcm=which("fcm")

        env["platform_config_dir"]="nci-x86-ifort"
        platform = "nci-x86-ifort"
        if "platform=oneapi" in spec:
            env["platform_config_dir"]="nci-x86-ifx"
            platform = "nci-x86-ifx"

        env["optimisation_level"]=spec.variants["opt"].value
        opt_value=spec.variants["opt"].value

        env["openmp"]="true"
        if "~omp" in spec:
            env["openmp"]="false"

        env["netcdf"] = "true"
        if "~netcdf" in spec:
            env["netcdf"] = "false"

        hg = 3 # build HadGEM3 ONLY here
        
        # Whether to build debug --jhan: adjust path to configs
        bld_config = f"bld-hadgem{hg}-mct.cfg"
        um_exe = f"um_hg${hg}.exe"
        if opt_value == "debug":
            bld_config = f"bld-dbg-hadgem{hg}-C2.cfg"
            um_exe = f"um_hg{hg}_dbg.exe-{opt_value}"

        bld_dir = f"ummodel_hg{hg}"
        # Build with fcm
        fcm("build", "-f", "-j", "4",
            join_path(bld_dir, "cfg", bld_config))

        # Install
        mkdirp(prefix.bin)
        install(
            join_path(bld_dir, "bin", um_exe),
            join_path(prefix.bin, um_exe))

        '''
        install("build-atmos/bin/um-atmos.exe", prefix.bin + "/um-atmos.exe")
        install("build-atmos/bin/um_script_functions", prefix.bin + "/um_script_functions")
        install("build-recon/bin/um-recon", prefix.bin + "/um-recon")
        install("build-recon/bin/um-recon.exe", prefix.bin + "/um-recon.exe")
        '''
