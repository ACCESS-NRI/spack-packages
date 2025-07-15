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
        # copy_tree(self.stage.source_path, prefix.src)
        src = self.stage.source_path
        dst = prefix.src
        tty.warn("Staging source.")
        tty.warn(f"src = {src}")
        tty.warn(f"dst = {dst}")
        shutil.copytree(src, dst)