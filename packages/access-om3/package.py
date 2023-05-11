# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class AccessOm3(BundlePackage):
    """Package which bundles all access-om3 spack package dependencies"""

    homepage = "https://www.github.com/COSIMA/access-om3"
    # There is no URL since there is no code to download.

    maintainers = ["micaeljtoliveira", "aekiss"]

    version("0.0.1")

    # Versions are hard-coded here to match current build requirements.
    depends_on("esmf@8.3.1+parallelio~pnetcdf")
    depends_on("fms@2022.04")
    depends_on("parallelio@2.5.9")

    # There is no need for install() since there is no code.
