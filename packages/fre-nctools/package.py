# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class FreNctools(AutotoolsPackage):
    """FRE-NCtools is a collection of tools for creating grids and mosaics
    commonly used in climate and weather models, the remapping of data among
    grids, and the creation and manipulation of netCDF files. These tools were
    largely written by members of the GFDL Modeling Systems Group primarily for
    use in the Flexible Modeling System (FMS) Runtime Environment (FRE)
    supporting the work of the Geophysical Fluid Dynamics Laboratory (GFDL)."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://github.com/NOAA-GFDL/FRE-NCtools"
    url = "https://github.com/NOAA-GFDL/FRE-NCtools/archive/2022.02.tar.gz"

    # FIXME: Add a list of GitHub accounts to
    # notify when the package is updated.
    # maintainers = ["github_user1", "github_user2"]

    version("2022.02", sha256="bd90c9c3becdb19ff408c0915e61141376e81c12651a5c1b054c75ced9a73ad2")

    variant("mpi", default=False, description="Builds with MPI support")
    
    depends_on("autoconf", type="build")
    depends_on("automake", type="build")
    depends_on("libtool", type="build")
    depends_on("netcdf-c")
    depends_on("netcdf-fortran")

    def configure_args(self):
        spec = self.spec

        args = ["--disable-ocean-model-grid-generator"]
        if "+mpi" in spec:
            args.append("--with-mpi")
        return args
