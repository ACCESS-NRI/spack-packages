# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import configparser
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
        values=("debug", "high", "rigorous", "safe"), multi=False)
    variant("platform", default="nci-x86-ifort", description="Site platform",
        values=("nci-x86-ifort", "vm-x86-gnu"), multi=False)


    depends_on("fcm", type="build")
    # For GCOM versions, see
    # https://code.metoffice.gov.uk/trac/gcom/wiki/Gcom_meto_installed_versions
    depends_on("gcom@7.8", when="@:13.0", type=("build", "link"))
    depends_on("gcom@7.9", when="@13.1", type=("build", "link"))
    depends_on("gcom@8.0", when="@13.2", type=("build", "link"))
    depends_on("gcom@8.1", when="@13.3", type=("build", "link"))
    depends_on("gcom@8.2", when="@13.4", type=("build", "link"))
    depends_on("gcom@8.3:", when="@13.5:", type=("build", "link"))
    depends_on("eccodes +fortran +netcdf", type=("build", "link", "run"))
    depends_on("netcdf-fortran@4.5.2", type=("build", "link", "run"))

    phases = ["build", "install"]

    # The dependency name and the ld_flags from
    # the FCM config for each library configured via FCM.
    _lib_cfg = {
        "DR_HOOK": {
            "dep_name": "drhook",
            "fcm_ld_flags": "-ldrhook"},
        "eccodes": {
            "dep_name": "eccodes",
            "fcm_ld_flags": "-leccodes_f90 -leccodes"},
        "netcdf": {
            "dep_name": "netcdf-fortran",
            "fcm_ld_flags": "-lnetcdff -lnetcdf"}}


    def _get_linker_args(self, spec, fcm_libname):
        """
        Return the linker flags corresponding to fcm_libname,
        a library name configured via FCM.
        """
        dep_name = self._lib_cfg[fcm_libname]["dep_name"]
        ld_flags = [
            spec[dep_name].libs.ld_flags,
            self._lib_cfg[fcm_libname]["fcm_ld_flags"]]
        # The reason for the explicit -rpath is:
        # https://github.com/ACCESS-NRI/spack_packages/issues/14#issuecomment-1653651447
        rpaths = ["-Wl,-rpath=" + d for d in spec[dep_name].libs.directories]

        # Both ld_flags and rpaths are lists of strings.
        return " ".join(ld_flags + rpaths)


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
        # The gcom library does not contain shared objects and
        # therefore must be statically linked.
        env.prepend_path("LIBRARY_PATH", spec["gcom"].prefix.lib)

        # Use rose-app.conf to set config options.
        config = configparser.ConfigParser()
        config.read(join_path(self.package_dir, "rose-app.conf"))
        # Modify the config as per points 8 and 9 of
        # https://metomi.github.io/rose/2019.01.8/html/api/configuration/rose-configuration-format.html
        for key in config["env"]:
            if len(key) > 0 and key[0] != '!':
                value = config["env"][key].replace("\n=", "\n")
                env.set(key, value)

        # Override some specific environment variables
        env.set("optimisation_level", spec.variants["optim"].value)
        env.set("platform_config_dir", spec.variants["platform"].value)
        env.set("um_rev", f"vn{spec.version}")
        components = ["casim", "jules", "shumlib", "socrates", "ukca"]
        for comp in components:
            env.set(f"{comp}_rev", f"um{spec.version}")
        for fcm_libname in ["eccodes", "netcdf"]:
            linker_args = self._get_linker_args(spec, fcm_libname)
            env.set(f"ldflags_{fcm_libname}_on", linker_args)


    def _build_dir(self):
        """
        Return the build directory.
        """
        return join_path(self.stage.source_path, "..", "spack-build")


    def build(self, spec, prefix):
        """
        Use FCM to build the executables.
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
        Install executables and accompanying files into the prefix directory,
        according to the directory structure of EXEC_DIR, as described in (e.g.)
        https://code.metoffice.gov.uk/trac/roses-u/browser/b/y/3/9/5/trunk/meta/rose-meta.conf
        """
        for um_exe in ["atmos", "recon"]:
            bin_dir = join_path(f"build-{um_exe}", "bin")
            build_bin_dir = join_path(self._build_dir(), bin_dir)
            install_bin_dir = join_path(prefix, bin_dir)
            mkdirp(install_bin_dir)
            install_tree(build_bin_dir, install_bin_dir)
