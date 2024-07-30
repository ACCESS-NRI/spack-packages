# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py
# and https://github.com/coecms/access-esm-build-gadi
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import configparser
import llnl.util.tty as tty
from spack.package import *

class Um(Package):
    """
    UM is a numerical weather prediction and climate modelling software package.
    """

    homepage = "https://code.metoffice.gov.uk/trac/um"
    svn = "file:///g/data/ki32/mosrs/um/main/trunk"

    # See 'fcm kp fcm:um.xm' for release versions
    version("13.0", revision=111272, preferred=True)
    version("13.1", revision=114076)
    version("13.2", revision=116723)
    version("13.3", revision=118802)
    version("13.4", revision=120750)
    version("13.5", revision=123226)
    version("13.6", revision=124981)

    maintainers("penguian")

    variant("optim", default="safe", description="Optimization level",
        values=("debug", "high", "rigourous", "safe"), multi=False)
    variant("platform", default="nci-x86-ifort", description="Site platform",
        values=("nci-x86-ifort", "vm-x86-gnu"), multi=False)
        

    depends_on("fcm", type="build")
    depends_on("openmpi@4.0.2:4.1.0", type=("build", "run"))
    depends_on("gcom", type=("build", "link"))
    depends_on("eccodes +fortran +netcdf", type=("build", "link"))
    depends_on("netcdf-fortran@4.5.2", type=("build", "link"))

    phases = ["build", "install"]


    def _get_linker_args(self, spec, libname):
        """
        The reason for the explicit -rpath is:
        https://github.com/ACCESS-NRI/spack_packages/issues/14#issuecomment-1653651447
        """
        ld_flags = spec[libname].libs.ld_flags
        rpaths = ["-Wl,-rpath=" + d for d in spec[libname].libs.directories]
        return " ".join([ld_flags] + rpaths)


    def setup_build_environment(self, env):
        """
        Set environment variables to their required values.
        """
        spec = self.spec
        env.prepend_path("PATH", spec["fcm"].prefix.bin)
        ideps = ["eccodes", "gcom", "netcdf-fortran"]
        incs = [spec[d].prefix.include for d in ideps]
        for ipath in incs:
            env.prepend_path("CPATH", ipath)
        """
        The gcom library does not contain shared objects and
        therefore must be statically linked.
        """
        env.prepend_path("LIBRARY_PATH", spec["gcom"].prefix.lib)

        #Set configuration options
        config = configparser.ConfigParser()
        config.read(join_path(self.package_dir, "rose-app.conf"))
        for key in config["env"]:
            if len(key) > 0 and key[0] != '!':
                value = config["env"][key].replace("\n=","\n") 
                env.set(key, value)

        # Override some specific environment variables
        env.set("optimisation_level", spec.variants["optim"].value)
        env.set("platform_config_dir", spec.variants["platform"].value)
        env.set("um_rev", f"vn{spec.version}")
        components = ["casim", "jules", "shumlib", "socrates", "ukca"]
        for comp in components:
            key = f"{comp}_rev"
            value = f"um{spec.version}"
            env.set(key, value)
        dep = {
                "drhook": "drhook",
                "eccodes": "eccodes",
                "netcdf": "netcdf-fortran"}
        extra_ld_flags = {
                "drhook": "-ldrhook",
                "eccodes": "-leccodes_f90 -leccodes",
                "netcdf": "-lnetcdff -lnetcdf"}
        for libname in ["eccodes", "netcdf"]:
            linker_args = " ".join([
                    extra_ld_flags[libname],
                    self._get_linker_args(spec, dep[libname])])
            env.set(f"ldflags_{libname}_on", linker_args)


    def _build_dir(self):
        """
        Return the build directory.
        """
        return join_path(self.stage.source_path, "..", "spack-build")


    def build(self, spec, prefix):
        """
        Use FCM to build the executable.
        """
        config_file = join_path(self.package_dir, "fcm-make.cfg")
        build_dir = self._build_dir()
        mkdirp(build_dir)
        fcm = which("fcm")
        fcm("make",
            "--new",
            f"--config-file={config_file}",
            f"--directory={build_dir}",
            "--jobs=4")


    def install(self, spec, prefix):
        """
        Install the executable into the prefix.bin directory.
        """
        mkdirp(prefix.bin)
        for component in ["atmos", "recon"]:
            bin_dir = join_path(
                    self._build_dir(), 
                    f"build-{component}", 
                    "bin")
            install_tree(bin_dir, prefix.bin)

