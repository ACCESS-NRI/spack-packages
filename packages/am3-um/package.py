from spack.package import *

class Am3Um(Package):
    """Experimental UM source-only package."""

    homepage = "https://github.com/ACCESS-NRI/UM"
    git = "git@github.com:ACCESS-NRI/UM.git"

    version('main', branch='AM3-dev')

    def install(self, spec, prefix):
        # Just copy the staged source to the prefix so that downstream packages can pick it up
        install_tree(self.stage.source_path, prefix.src)