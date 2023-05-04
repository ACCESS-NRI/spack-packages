# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2023 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class AccessOm2(BundlePackage):
    """ACCESS-OM2 bundle contains the coupled CICE5 and MOM5 models."""

    homepage = "https://www.access-nri.org.au"

    maintainers = ["harshula"]

    version("2023.01.001-1")

    depends_on("libaccessom2")
    depends_on("cice5")
    depends_on("mom5")

    # There is no need for install() since there is no code.
