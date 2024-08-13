# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import configparser
from spack.error import SpecError
from spack.package import *
import llnl.util.tty as tty

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

    variant("model", default="default", description="Model configuration.",
        values=("default", "access-ram3"), multi=False)
    variant("optim", default="none", description="Optimization level",
        values=("none", "debug", "high", "rigorous", "safe"), multi=False)
    variant("site_platform", default="none", description="Site platform",
        values="*", multi=False)

    _bool_off_variants = (
        "DR_HOOK",
        "platagnostic",
        "thread_utils")
    for b in _bool_off_variants:
        variant(b, default=False, description=b, multi=False)

    _bool_on_variants = (
        "eccodes",
        "netcdf",
        "openmp")
    for b in _bool_on_variants:
        variant(b, default=True, description=b, multi=False)

    _bool_variants = _bool_off_variants + _bool_on_variants

    _str_variants = (
        "casim_rev",
        "casim_sources",
        "compile_atmos",
        "compile_createbc",
        "compile_crmstyle_coarse_grid",
        "compile_pptoanc",
        "compile_recon",
        "compile_scm",
        "compile_sstpert_lib",
        "compile_wafccb_lib",
        "config_revision",
        "config_root_path",
        "config_type",
        "COUPLER",
        "extract",
        "fcflags_overrides",
        "gwd_ussp_precision",
        "jules_rev",
        "jules_sources",
        "land_surface_model",
        "ldflags_overrides_prefix",
        "ldflags_overrides_suffix",
        "ls_precipitation_precision",
        "mirror",
        "mpp_version",
        "portio_version",
        "prebuild",
        "recon_mpi",
        "shumlib_rev",
        "shumlib_sources",
        "socrates_rev",
        "socrates_sources",
        "stash_version",
        "timer_version",
        "ukca_sources",
        "ukca_rev",
        "um_sources")
    for v in _str_variants:
        variant(v, default="none", description=v, values="*", multi=False)

    depends_on("fcm site=nci-gadi", type="build")
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
        model = spec.variants["model"].value
        config_file = join_path(
            self.package_dir,
            "model",
            model,
            "rose-app.conf")
        config.read(config_file)

        # Modify the config as per points 8 and 9 of
        # https://metomi.github.io/rose/2019.01.8/html/api/configuration/rose-configuration-format.html
        config_env = dict()
        for key in config["env"]:
            if len(key) > 0 and key[0] != '!':
                config_env[key] = config["env"][key].replace("\n=", "\n")

        # Override the environment variables corresponding to
        # the optim and site_platform variants.
        optim = spec.variants["optim"].value
        if optim != "none":
            config_env["optimisation_level"] = optim
        site_platform = spec.variants["site_platform"].value
        if site_platform != "none":
            config_env["platform_config_dir"] = site_platform

        # Override the model UM revision based on the spec UM version.
        model_um_rev = config_env["um_rev"]
        spec_um_rev = f"vn{spec.version}"
        if model_um_rev != spec_um_rev:
            if model_um_rev != "":
                tty.warn(
                    f"The {model} model uses um_rev={um_rev} but"
                    f"the spec calls for um_rev={spec_um_rev}.\n"
                    f"Revision {spec_um_rev} will be used.")
            # Always use the UM revision based on the spec UM version.
            config_env["um_rev"] = spec_um_rev

        # Overide the model component revisions only when
        # the model leaves the revision unspecified.
        components = ["casim", "jules", "shumlib", "socrates", "ukca"]
        for comp in components:
            model_comp_rev = config_env[f"{comp}_rev"]
            spec_comp_rev = f"um{spec.version}"
            if model_comp_rev != spec_comp_rev:
                if model_comp_rev == "":
                    config_env[f"{comp}_rev"] = spec_comp_rev
                else:
                    tty.warn(
                        f"The {model} model uses {comp}_rev={comp_rev} but"
                        f"the spec implies {comp}_rev={spec_um_rev}.")

        # Override those environment variables corresponding to a bool variant.
        _bool_to_str = lambda b: "true" if b else "false"
        for b in self._bool_variants:
            config_env[b] = _bool_to_str(spec.variants[b].value)

        # Override those environment variables where a string variant is specified.
        for v in self._str_variants:
            v_value = spec.variants[v].value
            if v_value != "none":
                config_env[v] = v_value

        # Get the linker arguments for some dependencies.
        for fcm_libname in ["eccodes", "netcdf"]:
            linker_args = self._get_linker_args(spec, fcm_libname)
            config_env[f"ldflags_{fcm_libname}_on"] = linker_args

        # Set environment variables based on config_env.
        for key in config_env:
            env.set(key, config_env[key])


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

