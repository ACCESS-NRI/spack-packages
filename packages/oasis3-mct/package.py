# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
import sys
import os
import shutil
from pathlib import Path
from pprint import pprint

class Oasis3Mct(Package):
    """ACCESS-NRI's fork of https://gitlab.com/cerfacs/oasis3-mct OASIS3-MCT 2.0."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/oasis3-mct.git"

    # notify when the package is updated.
    maintainers = ["harshula"]

    version("5e57b1aa40840adb6d6747d475dabadab5d9d6fb", commit="5e57b1aa40840adb6d6747d475dabadab5d9d6fb")

    depends_on("netcdf-fortran@4.5.2:")
    depends_on("openmpi@4.0.2:")

    phases = ["build", "install"]

    def build(self, spec, prefix):
        # TODO: Need to rethink the build process. Likely require modifying
        #       oasis3-mct
        build = Executable("./build.sh")
        build()

    def install(self, spec, prefix):
        srcdir = os.path.join("compile_oa3-mct", "lib")
        dstdir = os.path.join(prefix, "usr", "lib")

        # TODO: Spack should have a way to find/create the installation path
        Path(dstdir).mkdir(parents=True, exist_ok=True)

        print(f"Installing files in {dstdir}", file=sys.stdout)
        # TODO: See if there's a better way to do this?!
        for f in ["libmct.a", "libmpeu.a", "libpsmile.MPI1.a", "libscrip.a"]:
            srcpath = os.path.join(srcdir, f)
            shutil.copy2(srcpath, dstdir)

        #print(os.environ)
        #pprint(dir(spec))
        #pprint(spec.__dict__, indent=2)
