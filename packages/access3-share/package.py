# Copyright 2013-2025 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

from spack.package import *


class Access3Share(CMakePackage):
    """Shared coupler/mediator libraries used by the ACCESS version 3 climate models. This 
    package includes the Community Mediator for Earth Prediction Systems (CMEPS) and Community 
    Data models for Earth Prediction Systems (CDEPS) as used in ACCESS-OM3 (and the future 
    ACCESS-CM3 and ACCESS-ESM3 etc). See Access3Exe package to produce executable programs."""

    homepage = "https://github.com/ACCESS-NRI/access3-share"
    git = "https://github.com/ACCESS-NRI/access3-share"
    submodules = True
    maintainers = ["anton-seaice", "harshula", "micaeljtoliveira"]

    license("Apache-2.0", checked_by="anton-seaice")

    variant("openmp", default=False, description="Enable OpenMP")

    depends_on("cmake@3.18:", type="build")
    depends_on("mpi")
    depends_on("netcdf-fortran@4.6.0:")
    depends_on("esmf@8.3.0:")
    depends_on("esmf cflags='-fp-model precise' fflags='-fp-model precise'", when="%intel")
    depends_on("esmf cflags='-fp-model precise' fflags='-fp-model precise'", when="%oneapi")
    depends_on("fortranxml@4.1.2:")

    depends_on("parallelio@2.5.10: build_type==RelWithDebInfo")
    depends_on("parallelio fflags='-qno-opt-dynamic-align -convert big_endian -assume byterecl -ftz -traceback -assume realloc_lhs -fp-model source' cflags='-qno-opt-dynamic-align -fp-model precise -std=gnu99'", when="%intel")
    depends_on("parallelio fflags='-qno-opt-dynamic-align -convert big_endian -assume byterecl -ftz -traceback -assume realloc_lhs -fp-model source' cflags='-qno-opt-dynamic-align -fp-model precise -std=gnu99'", when="%oneapi")

    def cmake_args(self):
        args = [
            self.define("ACCESS3_LIB_INSTALL", True),
            self.define_from_variant("OPENMP", "openmp"),
        ]

        return args