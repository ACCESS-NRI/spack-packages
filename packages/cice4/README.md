# Notes on building cice4 for ACCESS-ESM 1.5

For ACCESS-ESM 1.5, the cice4 executable that we are interested in in the one built by 
https://github.com/penguian/access-esm-build-gadi/blob/build-all-using-oasis3-new-modules-pbd562/Makefile

## Building `src/cice4.1`

The source code is the `ESM_1.5` branch of https://github.com/ACCESS-NRI/cice4, altered as follows

```
	sed -i 's/\([[:space:]]*setenv CPLLIBDIR\).*$$/\1 $$OASIS_LIB_DIR/' $@/compile/comp_access-cm_cice.RJ.nP-mct
	sed -i 's/\([[:space:]]*setenv CPLINCDIR\).*$$/\1 $$OASIS_INCLUDE_DIR/' $@/compile/comp_access-cm_cice.RJ.nP-mct
	rm -f $@/compile/environs.raijin.nci.org.au ; touch $@/compile/environs.raijin.nci.org.au
	cp patch/Macros.Linux.raijin.nci.org.au-mct $@/bld
```
The first two lines change the following two lines of https://github.com/ACCESS-NRI/cice4/blob/ESM_1.5/compile/comp_access-cm_cice.RJ.nP-mct
```
  setenv CPLLIBDIR /projects/access/apps/oasis3-mct/ompi.1.10.2/lib
  setenv CPLINCDIR /projects/access/apps/oasis3-mct/ompi.1.10.2/include
```
to use `$OASIS_LIB_DIR` and `$OASIS_INCLUDE_DIR` instead. These resolve to
```
export OASIS_INCLUDE_DIR=$${PWD}/lib/oasis/include
export OASIS_LIB_DIR=$${PWD}/lib/oasis/lib
```
respectively, with `lib/oasis` obtained and built from the `new_modules_pbd562` branch of https://github.com/penguian/oasis3-mct

The third line removes the environment setup script https://github.com/ACCESS-NRI/cice4/blob/ESM_1.5/compile/environs.raijin.nci.org.au so that 
the `access-esm-build-gadi` `ENVFILE` script `./environment.sh` is used instead.

The fourth line copies the Makefile macro file `patch/Macros.Linux.raijin.nci.org.au-mct` into the `bld` directory so that the following lines in
https://github.com/ACCESS-NRI/cice4/blob/ESM_1.5/compile/comp_access-cm_cice.RJ.nP-mct can work with `ARCH` set to `raijin.nci.org.au`:
```
gmake VPFILE=Filepath EXEC=$BINDIR/$EXE \
           NXGLOB=$NXGLOB NYGLOB=$NYGLOB \
           N_ILYR=$N_ILYR \
           BLCKX=$BLCKX BLCKY=$BLCKY MXBLCKS=$MXBLCKS \
      -f  $CBLD/Makefile MACFILE=$CBLD/Macros.Linux.${ARCH}-mct || exit 2
```

## Building `bin/cice-12p`

The `access-esm-build-gadi` `Makefile` builds `bin/cice-12p` using the single line
```
source $(ENVFILE) ; cd $</compile ; csh ./comp_access-cm_cice.RJ.nP-mct 12
```
so that the script file https://github.com/ACCESS-NRI/cice4/blob/ESM_1.5/compile/comp_access-cm_cice.RJ.nP-mct is called with `$1 == 12`, which sets `nproc = 12`.

