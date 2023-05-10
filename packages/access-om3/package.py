# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install access-om3
#
# You can edit this file again by typing:
#
#     spack edit access-om3
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class AccessOm3(BundlePackage):
    """FIXME: Put a proper description of your package here."""

    homepage = "https://www.github.com/COSIMA/access-om3"
    # There is no URL since there is no code to download.

    maintainers = ["micaeljtoliveira", "aekiss"]

    version("0.0.1")

    # FIXME: Add dependencies if required.
    depends_on("esmf@8.3.1+parallelio~pnetcdf")
    depends_on("fms@2022.04")
    depends_on("parallelio@2.5.9")

    # There is no need for install() since there is no code.
