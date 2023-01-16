# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import install, join_path, mkdirp

# https://spack.readthedocs.io/en/latest/build_systems/makefilepackage.html
class Cice5(MakefilePackage):
    """The Los Alamos sea ice model (CICE) is the result of an effort to develop a computationally efficient sea ice component for a fully coupled atmosphere-land global climate model."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/cice5.git"

    maintainers = ["harshula"]

    version("spack-build", branch="spack-build")

    # TODO: Should we depend on virtual package "mpi" instead?
    depends_on("openmpi@4.0.2:")
    depends_on("oasis3-mct")
    depends_on("datetime-fortran")
    depends_on("netcdf-fortran@4.5.2:")
    depends_on("netcdf-c@4.7.4:")
    # cice5 builds parallelio with -DWITH_PNETCDF=OFF -DPIO_ENABLE_TIMING=OFF
    depends_on("parallelio")
    depends_on("libaccessom2")

    phases = ["build", "install"]

    # The integr represents environment variable NTASK
    __targets = {24: {}, 480: {}, 722: {}, 1682: {}}
    __targets[24]["RES"] = "360x300"
    __targets[24]["BLCKX"] = 360 // 24
    __targets[24]["BLCKY"] = 300 // 1

    __targets[480]["RES"] = "1440x1080"
    __targets[480]["BLCKX"] = 1440 // 48
    __targets[480]["BLCKY"] = 1080 // 40

    # Comment from bld/config.nci.auscom.3600x2700:
    # Recommendations:
    #   use processor_shape = slenderX1 or slenderX2 in ice_in
    #   one per processor with distribution_type='cartesian' or
    #   squarish blocks with distribution_type='rake'
    # If BLCKX (BLCKY) does not divide NXGLOB (NYGLOB) evenly, padding
    # will be used on the right (top) of the grid.
    __targets[722]["RES"] = "3600x2700"
    __targets[722]["BLCKX"] = 3600 // 90
    __targets[722]["BLCKY"] = 2700 // 90

    __targets[1682]["RES"] = "18x15.3600x2700"
    __targets[1682]["BLCKX"] = 3600 // 200
    __targets[1682]["BLCKY"] = 2700 // 180


    def build(self, spec, prefix):

        incs = (spec["oasis3-mct"].headers).cpp_flags + "/psmile.MPI1" + " "
        for l in ["parallelio", "oasis3-mct", "libaccessom2", "netcdf-fortran"]:
            incs += (spec[l].headers).cpp_flags + " "

        # NOTE: The order of the libraries matter during the linking step!
        # NOTE: datetime-fortran is a dependency of libaccessom2.
        libs = "-L" + (spec["parallelio"].prefix) + "/lib -lpiof -lpioc "
        for l in ["oasis3-mct", "libaccessom2", "netcdf-c", "netcdf-fortran", "datetime-fortran"]:
            libs += (spec[l].libs).ld_flags + " "

        build = Executable("bld/build.sh")
        build.add_default_env("CPL_INCS", incs)
        build.add_default_env("CPLLIBS", libs)

        for k in self.__targets:
            build.add_default_env("NTASK", str(k))
            build.add_default_env("RES", self.__targets[k]["RES"])
            build.add_default_env("BLCKX", str(self.__targets[k]["BLCKX"]))
            build.add_default_env("BLCKY", str(self.__targets[k]["BLCKY"]))
            build("nci", "auscom", self.__targets[k]["RES"])


    def install(self, spec, prefix):

        mkdirp(prefix.bin)
        install(join_path("build_auscom_360x300_24p", "cice_auscom_360x300_24p.exe"), prefix.bin)
        install(join_path("build_auscom_1440x1080_480p", "cice_auscom_1440x1080_480p.exe"), prefix.bin)
        install(join_path("build_auscom_3600x2700_722p", "cice_auscom_3600x2700_722p.exe"), prefix.bin)
