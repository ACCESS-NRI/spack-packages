# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
# Based on https://github.com/nci/spack-repo/blob/main/packages/um/package.py
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import configparser
from spack.package import *
import llnl.util.tty as tty

class Um(Package):
    """
    UM is a numerical weather prediction and climate modelling software package.
    """

    homepage = "https://code.metoffice.gov.uk/trac/um"
    svn = "file:///g/data/ki32/mosrs/um/main/trunk"

    # See 'fcm kp fcm:um.xm' for release versions.
    _revision = {
        "13.0": 111272,
        "13.1": 114076,
        "13.2": 116723,
        "13.3": 118802,
        "13.4": 120750,
        "13.5": 123226,
        "13.6": 124981}
    _max_minor = 6
    version("13.0", revision=_revision["13.0"], preferred=True)
    for v in range(1, 1 + _max_minor):
        _version = f"13.{v}"
        version(_version, revision=_revision[_version])

    maintainers("penguian")

    variant("model", default="vn13", description="Model configuration.",
        values=("vn13", "vn13p0-rns", "vn13p5-rns"), multi=False)

    # Bool variants have their default value set to True here.
    _bool_variants = (
        "eccodes",
        "netcdf")
    for var in _bool_variants:
        variant(var, default=True, description=var)

    # Off/on variants have 3-value "none" "off", "on" logic.
    _off_on_variants = (
        "openmp",
        "platagnostic",
        "thread_utils")
    for var in _off_on_variants:
        variant(var, default="none", description=var,
            values=("none", "off", "on"), multi=False)

    # String variants have their default values set to "none" here.
    # The real default is set by the model.
    _rev_variants = (
        "casim_rev",
        "jules_rev",
        "shumlib_rev",
        "socrates_rev",
        "ukca_rev")

    _other_str_variants = (
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
        "jules_sources",
        "land_surface_model",
        "ldflags_overrides_prefix",
        "ldflags_overrides_suffix",
        "ls_precipitation_precision",
        "mirror",
        "mpp_version",
        "optimisation_level",
        "platform_config_dir",
        "portio_version",
        "prebuild",
        "recon_mpi",
        "shumlib_sources",
        "socrates_sources",
        "stash_version",
        "timer_version",
        "ukca_sources",
        "um_sources")
    _str_variants = _rev_variants + _other_str_variants

    for var in _str_variants:
        variant(var, default="none", description=var, values="*", multi=False)

    # The 'site=nci-gadi' variant of fcm defines the keywords
    # used by the FCM configuration of UM.
    depends_on("fcm site=nci-gadi", type="build")

    # For GCOM versions, see
    # https://code.metoffice.gov.uk/trac/gcom/wiki/Gcom_meto_installed_versions
    depends_on("gcom@7.8", when="@:13.0", type=("build", "link"))
    depends_on("gcom@7.9", when="@13.1", type=("build", "link"))
    depends_on("gcom@8.0", when="@13.2", type=("build", "link"))
    depends_on("gcom@8.1", when="@13.3", type=("build", "link"))
    depends_on("gcom@8.2", when="@13.4", type=("build", "link"))
    depends_on("gcom@8.3:", when="@13.5:", type=("build", "link"))
    depends_on("eccodes +fortran +netcdf", type=("build", "link", "run"),
        when="+eccodes")
    depends_on("netcdf-fortran@4.5.2", type=("build", "link", "run"),
        when="+netcdf")

    phases = ["build", "install"]

    # The dependency name and the ld_flags from
    # the FCM config for each library configured via FCM.
    _lib_cfg = {
        "eccodes": {
            "dep_name": "eccodes",
            "fcm_ld_flags": "-leccodes_f90 -leccodes"},
        "netcdf": {
            "dep_name": "netcdf-fortran",
            "fcm_ld_flags": "-lnetcdff -lnetcdf"}}


    def _config_file_path(self, model):
        """
        Return the pathname of the Rose app config file
        corresponding to model.
        """
        return join_path(
            self.package_dir, "model", model, "rose-app.conf")


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

        def check_model_vs_spec(model, config_env, var, spec_value):
            """
            Check whether the value spec_value for the variant var
            agrees with the model's configured value config_env[var],
            and produce an appropriate warning or debug message.
            """
            if var not in config_env:
                tty.warn(
                    f"The {model} model does not specify {var}. "
                    f"The value {spec_value} will be used.")
            else:
                model_value = config_env[var]
                if model_value != "" and model_value != spec_value:
                    tty.warn(
                        f"The {model} model sets {var}={model_value} but "
                        f"the spec sets {var}={spec_value}. "
                        f"The value {spec_value} will be used.")


        spec = self.spec

        # Define CPATH for dependencies that need include files.
        ideps = ["eccodes", "gcom", "netcdf-fortran"]
        incs = [spec[d].prefix.include for d in ideps]
        for ipath in incs:
            env.prepend_path("CPATH", ipath)

        # The gcom library does not contain shared objects and
        # therefore must be statically linked.
        env.prepend_path("LIBRARY_PATH", spec["gcom"].prefix.lib)

        # Use rose-app.conf to set config options.
        config = configparser.ConfigParser()
        # Ensure that keys are case sensitive.
        # https://docs.python.org/3/library/configparser.html#customizing-parser-behaviour
        config.optionxform = lambda option: option
        model = spec.variants["model"].value
        config.read(self._config_file_path(model))

        # Modify the config as per points 8 and 9 of
        # https://metomi.github.io/rose/2019.01.8/html/api/configuration/rose-configuration-format.html
        config_env = dict()
        for key in config["env"]:
            if len(key) > 0 and key[0] != '!':
                config_env[key] = config["env"][key].replace("\n=", "\n")

        # Override the model UM revision based on the spec UM version.
        key = "um_rev"
        spec_um_rev = f"vn{spec.version}"
        check_model_vs_spec(model, config_env, key, spec_um_rev)
        config_env[key] = spec_um_rev

        # Overide each model component revision as the default
        # *only when the model leaves the revision unspecified*.
        for key in self._rev_variants:
            version_comp_rev = f"um{spec.version}"
            if key not in config_env or config_env[key] == "":
                config_env[key] = version_comp_rev
            else:
                model_comp_rev = config_env[key]
                if model_comp_rev != version_comp_rev:
                    tty.warn(
                        f"The {model} model sets {key}={model_comp_rev} but "
                        f"the spec implies {key}={version_comp_rev}. "
                        f"Revision {model_comp_rev} will be used as the default.")

        # Set DR_HOOK="false" until this package is available.
        config_env["DR_HOOK"] = "false"

        # Override those environment variables where a bool variant is specified.
        bool_to_str = lambda b: "true" if b else "false"
        for var in self._bool_variants:
            spec_str_value = bool_to_str(spec.variants[var].value)
            check_model_vs_spec(model, config_env, var, spec_str_value)
            config_env[var] = spec_str_value

        # Override those environment variables where an off/on variant is specified.
        off_on_to_str = lambda off_on: "true" if off_on == "on" else "false"
        for var in self._off_on_variants:
            spec_value = spec.variants[var].value
            if spec_value != "none":
                spec_str_value = off_on_to_str(spec_value)
                check_model_vs_spec(model, config_env, var, spec_str_value)
                config_env[var] = spec_str_value

        # Override those environment variables where a string variant is specified.
        for var in self._str_variants:
            spec_value = spec.variants[var].value
            if spec_value != "none":
                check_model_vs_spec(model, config_env, var, spec_value)
                config_env[var] = spec_value

        # Get the linker arguments for some dependencies.
        for fcm_libname in ["eccodes", "netcdf"]:
            linker_args = self._get_linker_args(spec, fcm_libname)
            config_env[f"ldflags_{fcm_libname}_on"] = linker_args

        # Set environment variables based on config_env.
        for key in config_env:
                tty.info(f"{key}={config_env[key]}")
                env.set(key, config_env[key])

        # Add the location of the FCM executable to PATH.
        env.prepend_path("PATH", spec["fcm"].prefix.bin)


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

