# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
# ----------------------------------------------------------------------------
#
#     spack install access-triangle-git
#
# You can edit this file again by typing:
#
#     spack edit access-triangle-git
#
# ----------------------------------------------------------------------------

from spack.package import *
import glob
import os


class AccessTriangleGit(MakefilePackage):
    """Example Spack package for the ISSM Triangle library."""

    homepage = "https://github.com/ACCESS-NRI/issm-triangle"
    url      = "https://github.com/ACCESS-NRI/issm-triangle/archive/refs/heads/main.tar.gz"

    version('1.6', sha256='7adf2d6aa5b51cd6090e40109d48ec4f45aa545d06ce7ccde313b1e086855107')

    # If on some systems 'gmake' is truly required, keep it. Otherwise, 'make'
    # is often sufficient because Spack sets MAKE appropriately.
    depends_on('gmake',  type='build')
    depends_on('libx11', type='link')

    # MakefilePackage defaults:
    #   build_targets   = [] (e.g. ['all'])
    #   install_targets = []
    #
    # If your Makefile uses something like `make shared`, we set that:
    build_targets = ['shared']

    def edit(self, spec, prefix):
        """
        This stage is where you typically patch or customize the makefile.
        If the package comes with a pre-written Makefile that needs minimal
        changes, you can do them here. Below, we just copy in the 'configs'
        so that the build can find them in `self.build_directory`.
        """
        install('configs/makefile',         self.build_directory)
        install('configs/linux/configure.make', self.build_directory)

    def install(self, spec, prefix):
        """
        The MakefilePackage base class will run `make` and `make <build_targets>`
        in `build()`. So here in `install()` we only need to copy the resulting
        artifacts to the install prefix.
        """
        # Ensure the standard directories exist
        mkdirp(prefix.include)
        mkdirp(prefix.lib)
        mkdirp(prefix.bin)
        mkdirp(prefix.share)

        # We assume the build puts libs in the build dir or top-level
        with working_dir(self.build_directory):
            for libfile in glob.glob("libtriangle.*"):
                install(libfile, prefix.lib)

            # Install headers if they exist in the build directory
            if os.path.exists('triangle.h'):
                install('triangle.h', prefix.include)

        # If there is a 'bin' subdirectory with executables:
        if os.path.isdir('bin'):
            for binfile in glob.glob("bin/*"):
                install(binfile, prefix.bin)

        # If there is a 'share' subdirectory for docs/data:
        if os.path.isdir('share'):
            for sharefile in glob.glob("share/*"):
                install(sharefile, prefix.share)
