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
    version("7.3", branch="main", preferred=True)
    version("access-esm1.5", branch="access-esm1.5")

    maintainers("penguian")

    depends_on("dummygrib", type=("build", "link"))
    depends_on("fcm", type="build")
    depends_on("gcom4@access-esm1.5+mpi", type=("build", "link"))
    depends_on("openmpi@4.0.2:4.1.0", type=("build", "run"))
    depends_on("netcdf-fortran@4.5.1:4.5.2", type=("build", "link"))
    depends_on("oasis3-mct@access-esm1.5", type=("build", "link"))

    variant("omp", default=True, description="Use OpenMP")
    variant("netcdf", default=True, description="NetCDF")
    variant("opt", default="high", description="Optimization level",
            values=("high", "debug"), multi=False)


    def setup_build_environment(self, env):
        env.prepend_path("PATH", self.spec["fcm"].prefix.bin)
        env.prepend_path("CPATH", self.spec["gcom4"].prefix.include)
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
        env.prepend_path("LIBRARY_PATH", self.spec["netcdf-fortran"].prefix.lib)
        env.prepend_path("LIBRARY_PATH", self.spec["oasis3-mct"].prefix.lib)


    def setup_run_environment(self, env):
        env.prepend_path("LD_LIBRARY_PATH", self.spec["netcdf-fortran"].prefix.lib)


    def _bld_path(self):
        """
        Return the path to the build directory.
        """
        return "ummodel_hg3"


    def _bld_cfg_path(self, opt_value):
        """
        Return the path to the build configuration, depending on opt_value.
        """
        if opt_value == "debug":
            bld_config = "bld-dbg-hadgem3-C2.cfg"
        else:
            bld_config = "bld-hadgem3-mct.cfg"
        return join_path(self._bld_path(), "cfg", bld_config)


    def _exe_name(self, opt_value):
        """
        Return the executable name, depending on opt_value.
        """
        if opt_value == "debug":
            return "um_hg3_dbg.exe"
        else:
            return "um_hg3.exe"


    def patch(self):
        """
        Perform the equivalent of the following Bash and Sed commands,
        depending on the value of the "opt" variant:
        if "opt=debug"; then
            sed -i 's/-xHost //' $@/ummodel_hg3/cfg/bld-dbg-hadgem3-C2.cfg
        else
            sed -i 's/-xHost/-xCORE-AVX512/' $@/ummodel_hg3/cfg/bld-hadgem3-mct.cfg
        fi
        """
        opt_value = self.spec.variants["opt"].value
        bld_cfg_path = self._bld_cfg_path(opt_value)
        if opt_value == "debug":
            filter_file(r"-xHost ", "", bld_cfg_path)
        else:    
            filter_file(r"-xHost", "-xCORE-AVX512", bld_cfg_path)


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

        # Build with fcm
        fcm("build", "-f", "-j", "4", self._bld_cfg_path(opt_value))

        # Executable name depends on opt_value.
        um_exe = self._exe_name(opt_value)

        # Install
        mkdirp(prefix.bin)
        install(
            join_path(self._bld_path(), "bin", um_exe),
            join_path(prefix.bin, um_exe))

