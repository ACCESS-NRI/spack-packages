from spack.package import *
import llnl.util.tty as tty
import shutil

class Am3Um(Package):
    """Experimental UM source-only package."""

    homepage = "https://github.com/ACCESS-NRI/UM"
    git = "git@github.com:ACCESS-NRI/UM.git"

    version('main', branch='AM3-dev')

    phases = ["stage_source"]

    def build(self, spec, prefix):
        tty.warn("Source only, skipping build")

    def stage_source(self, spec, prefix):
        # Just copy the staged source to the prefix so that downstream packages can pick it up
        tty.warn("Staging source.")
        shutil.copytree(self.stage.source_path, prefix.src, dirs_exist_ok=True)