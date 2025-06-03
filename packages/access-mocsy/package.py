# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# Copyright 2024 ACCESS-NRI
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import find_libraries, install, join_path, mkdirp

# https://spack.readthedocs.io/en/latest/build_systems/makefilepackage.html
class AccessMocsy(MakefilePackage):
    """Routines to model ocean carbonate system thermodynamics. ACCESS NRI's fork."""

    homepage = "https://www.access-nri.org.au"
    git = "https://github.com/ACCESS-NRI/mocsy.git"

    maintainers("harshula")

    version("master", branch="master")
    version("gtracers", branch="gtracers", preferred=True)
    # TODO: Remove the 'mom5' version. The 'gtracers' version/branch is a copy of 'mom5'.
    version("mom5", branch="mom5")

    # Need: self.spec["mpi"].mpifc
    depends_on("mpi")

    _header = join_path("src", "mocsy_DNADHeaders.h")
    _libname = "libmocsy.a"
    _pcfile = "mocsy.pc"
    _pkgdir = "pkgconfig"
    _modfiles = [
        "dual_num_auto_diff.mod",
        "mocsy_buffesm.mod",
        "mocsy_constants.mod",
        "mocsy_depth2press.mod",
        "mocsy_derivauto.mod",
        "mocsy_derivnum.mod",
        "mocsy_errors.mod",
        "mocsy_f2pco2.mod",
        "mocsy_gasx.mod",
        "mocsy_p2fco2.mod",
        "mocsy_p80.mod",
        "mocsy_phsolvers.mod",
        "mocsy_rho.mod",
        "mocsy_rhoinsitu.mod",
        "mocsy_singledouble.mod",
        "mocsy_sw_adtg.mod",
        "mocsy_sw_ptmp.mod",
        "mocsy_sw_temp.mod",
        "mocsy_tis.mod",
        "mocsy_tpot.mod",
        "mocsy_vars.mod",
        "mocsy_varsolver.mod",
    ]

    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/mocsy/tarball/{0}".format(version)

    @property
    def libs(self):
        return find_libraries(
            "libmocsy", root=self.prefix, shared=False, recursive=True
        )

    def _create_pkgconf(self, spec, prefix):

        text = f"""\
prefix={prefix}
exec_prefix=${{prefix}}
libdir=${{exec_prefix}}/lib
includedir=${{prefix}}/include

Name: mocsy
Description: Routines to model ocean carbonate system thermodynamics.
Version: 2024.08.1
Libs: -L${{libdir}} -lmocsy
Cflags: -I${{includedir}}
Fflags: -I${{includedir}}
"""

        with open(join_path(self.stage.source_path, self._pcfile), "w", encoding="utf-8") as pc:
            nchars_written = pc.write(text)

        if nchars_written < len(text):
            raise OSError

    def build(self, spec, prefix):
        build = Executable("make")
        build(
            self._libname,
            "FC=" + self.spec["mpi"].mpifc,
            # Copied from MOM5/bin/mkmf.template.nci
            "FCFLAGS=-fno-alias -safe-cray-ptr -fpe0 -ftz -assume byterecl -i4 -r8 -traceback -nowarn -check noarg_temp_created -assume nobuffered_io -convert big_endian -grecord-gcc-switches -align all -g3 -O2 -xCORE-AVX2 -debug all -check none",
            "F90=" + self.spec["mpi"].mpifc
        )
        self._create_pkgconf(spec, prefix)

    def install(self, spec, prefix):

        # Creates prefix.lib too
        pkgconfdir = join_path(prefix.lib, self._pkgdir)
        mkdirp(pkgconfdir)
        mkdirp(prefix.include)

        install(join_path(self.stage.source_path, self._libname), prefix.lib)
        install(join_path(self.stage.source_path, self._header), prefix.include)
        for f in self._modfiles:
            install(join_path(self.stage.source_path, f), prefix.include)
        install(join_path(self.stage.source_path, self._pcfile), pkgconfdir)

