from spack.package import *

class Am3Jules(Package):
    """Experimental JULES source-only package."""

    homepage = "https://github.com/ACCESS-NRI/JULES"
    git = "git@github.com:ACCESS-NRI/JULES.git"

    version('main', branch='AM3-dev')

    def install(self, spec, prefix):
        # Just copy the staged source to the prefix so that downstream packages can pick it up
        install_tree(self.stage.source_path, prefix.src)