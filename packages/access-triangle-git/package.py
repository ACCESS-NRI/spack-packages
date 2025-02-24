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


class AccessTriangleGit(Package):

    homepage = "https://github.com/ACCESS-NRI/issm-triangle.git"
    url = "https://github.com/ACCESS-NRI/issm-triangle/archive/refs/heads/main.tar.gz"

    version('1.6', sha256='7adf2d6aa5b51cd6090e40109d48ec4f45aa545d06ce7ccde313b1e086855107')
    depends_on("libx11", type="link")
    depends_on("gmake", type="build")


    def edit(self, spec, prefix):

        install('configs/makefile', self.build_directory)
        install('configs/linux/configure.make', self.build_directory)


    def build(self, spec, prefix):
        make('shared')

    def install(self, spec, prefix):
        mkdirp(prefix.include, prefix.lib)
        
        for libfile in glob.glob("libtriangle.*"):
            install(libfile, prefix.lib)
            
        install('triangle.h', prefix.include)


