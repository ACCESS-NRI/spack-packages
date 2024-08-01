# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import find_libraries

class AccessGenericTracers(CMakePackage):
    """This is a fork of the NOAA-GFDL/ocean_BGC repo managed by NOAA-GFDL.
    It contains a collection of tracers and associated code for use with
    the MOM and GOLD ocean models. This fork includes generic tracer
    implementations of the suite of WOMBAT models used in ACCESS earth-system
    models."""

    homepage = "https://github.com/ACCESS-NRI/GFDL-generic-tracers"
    git = "https://github.com/ACCESS-NRI/GFDL-generic-tracers.git"

    maintainers("harshula")

    version("master", branch="master", preferred=True)
    version("development", branch="development")

    depends_on("access-mocsy")
    depends_on("access-fms")
    depends_on("mpi")

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/GFDL-generic-tracers/tarball/{0}".format(version)

    @property
    def libs(self):
        libraries = find_libraries(
            "libgtracers", root=self.prefix, shared=False, recursive=True
        )
        # mocsy is an internal lib dependency of this static library.
        # Hence we need to propagate it.
        return libraries + self.spec["access-mocsy"].libs

    def cmake_args(self):
        args = []
        args.append(self.define("CMAKE_C_COMPILER", self.spec["mpi"].mpicc))
        args.append(self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx))
        args.append(self.define("CMAKE_Fortran_COMPILER", self.spec["mpi"].mpifc))
        return args
