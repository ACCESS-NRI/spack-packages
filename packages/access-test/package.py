# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class AccessTest(BundlePackage):
    """ACCESS-TEST bundle is for testing ACCESS-NRI infrastructure."""

    homepage = "https://www.access-nri.org.au"

    git = "https://github.com/ACCESS-NRI/ACCESS-TEST.git"

    maintainers("harshula")

    version("latest")

    variant("deterministic", default=False, description="Deterministic build.")

    depends_on("oasis3-mct+deterministic", when="+deterministic", type="run")
    depends_on("oasis3-mct~deterministic", when="~deterministic", type="run")

    # There is no need for install() since there is no code.