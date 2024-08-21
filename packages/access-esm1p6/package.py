# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class AccessEsm1p6(BundlePackage):
    """ACCESS-ESM1.6 bundle contains the coupled UM7, CICE4 and MOM5 models.

    ACCESS-ESM1.6 comprises of:

    * The UKMO UM atmospheric model (v7.3), in the same configuration as
      ACCESS1.4, at N96 (1.875×1.25 degree), 38 level resolution
    * The CABLE land surface model with biogeochemistry (CASA-CNP) (CABLE2.4)
    * The GFDL MOM5 ocean model at 1 degree resolution
    * The WOMBATlite ocean BGC model (generic tracer version)
    * The LANL CICE4.1 sea ice model (version as ACCESS1.4)
    * The OASIS-MCT coupler
    """

    homepage = "https://www.access-nri.org.au"

    git = "https://github.com/ACCESS-NRI/ACCESS-ESM1.6.git"

    maintainers("dougiesquire")

    version("latest")

    depends_on("cice4@access-esm1.5", type="run")
    depends_on("mom5@access-esm1.6 type=ACCESS-ESM", type="run")
    # um7 is in a private repository
    depends_on("um7@access-esm1.5", type="run")

    # There is no need for install() since there is no code.
