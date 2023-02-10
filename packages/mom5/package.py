# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import install, join_path, mkdirp

# https://spack.readthedocs.io/en/latest/build_systems/makefilepackage.html
class Mom5(MakefilePackage):
    """MOM is a numerical ocean model based on the hydrostatic primitive equations."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/mom5.git"

    maintainers = ["harshula"]

    version("spack-build", branch="spack-build")

    # TODO: Should we depend on virtual package "mpi" instead?
    depends_on("openmpi@4.0.2:")
    depends_on("oasis3-mct")
    depends_on("datetime-fortran")
    depends_on("netcdf-fortran@4.5.2:")
    depends_on("netcdf-c@4.7.4:")
    # TODO: For initial verification we are going to use static pio.
    #       Eventually we plan to move to shared pio
    # ~shared requires: https://github.com/spack/spack/pull/34837
    depends_on("parallelio~pnetcdf~timing~shared")
    depends_on("libaccessom2")
    depends_on("hdf5")

    phases = ["build", "install"]

    def build(self, spec, prefix):

        incs = (spec["oasis3-mct"].headers).cpp_flags + "/psmile.MPI1" + " "
        for l in ["parallelio", "oasis3-mct", "libaccessom2", "netcdf-fortran"]:
            incs += (spec[l].headers).cpp_flags + " "

        # NOTE: The order of the libraries matter during the linking step!
        # NOTE: datetime-fortran is a dependency of libaccessom2.
        libs = "-L" + (spec["parallelio"].prefix) + "/lib -lpiof -lpioc "
        for l in ["oasis3-mct", "libaccessom2", "netcdf-c", "netcdf-fortran", "datetime-fortran"]:
            libs += (spec[l].libs).ld_flags + " "

        # cd ${ACCESS_OM_DIR}/src/mom/exp
        # export mom_type=ACCESS-OM
        # ./MOM_compile.csh --type $mom_type --platform spack

        # cppDefs = "-Duse_netCDF -Duse_netCDF3 -Duse_libMPI -DUSE_OCEAN_BGC -DENABLE_ODA -DSPMD -DLAND_BND_TRACERS"
        # set executable    = $root/exec/$platform/$type/fms_$type.x
        # set srcList = ( accessom_coupler )
        # set includes = "-I$executable:h:h/lib_FMS -I$executable:h:h/$type/lib_ocean"
        # set libs = "$executable:h:h/$type/lib_ocean/lib_ocean.a $executable:h:h/lib_FMS/lib_FMS.a"
        # bin/mkmf -f -m Makefile -a src -t bin/mkmfs.template.spack -p $executable:t" -o "$includes" -c "$cppDefs" -l "$libs"  $srcList

        with working_dir(join_path(self.stage.source_path, "exp")):
            build = Executable("./MOM_compile.csh")
            build.add_default_env("MOMINCS", incs)
            build.add_default_env("MOMLIBS", libs)
            build.add_default_env("MOMFC", "mpifort")
            build.add_default_env("MOMCC", "gcc")
            # Intel: setenv mpirunCommand   "mpirun --mca orte_base_help_aggregate 0 -np"
            # gfortran: setenv mpirunCommand   "mpirun -np"
            build.add_default_env("mpirunCommand", "mpirun -np")
            build("--type", "ACCESS-OM", "--platform", "spack")

    def install(self, spec, prefix):

        platform = "spack"
        mom_type = "ACCESS-OM"

        mkdirp(prefix.bin)
        install(
            join_path("exec", platform, mom_type, "fms_" + mom_type + ".x"),
            prefix.bin
        )
        install(join_path("bin", "mppnccombine." + platform), prefix.bin)
