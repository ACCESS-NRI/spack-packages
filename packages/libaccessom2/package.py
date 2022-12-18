# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2022 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Libaccessom2(CMakePackage):
    """libaccessom2 is a library that is linked into all of the ACCESS-OM2 component models, including YATM, CICE and MOM. libaccessom2 provides functionality used by all models as well as providing a interface to inter-model communication and synchronisation tasks. Using a common library reduces code duplication and provides a uniform way for all models to be integrated into ACCESS-OM2."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/libaccessom2.git"

    maintainers = ["harshula"]

    version("spack-build", branch="spack-build")

    depends_on("cmake@3.6:")
    depends_on("pkgconf")
    # TODO: Should we depend on virtual package "mpi" instead?
    depends_on("openmpi@4.0.2:")
    depends_on("oasis3-mct")
    depends_on("datetime-fortran")
    depends_on("json-fortran")
    depends_on("netcdf-fortran@4.5.2:")

