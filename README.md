## oe-deptools

A few scripts for working with Yocto/OpenEmbedded and Linux.

###  Installing

To install, clone the repo with git:

        git clone git://github.com/chbae/oe-deptools.git

You'll get a python script

* oey.py

You can copy the scripts to a standard location in your path or just
run them specifying the full path everytime (./oy.py <args>)

###  oey.py

Used to show dependencies for Yocto/OE packages.
 
#####  Help

        oey.py -h

        Usage: oey.py [options] [package]

        Displays dependencies for a given package or recipe.
        Uses either pn-depends.dot or package-depends.dot for its raw data.
        Generate the *.dot files by running bitbake -g <recipe>.

        Options:
        -h      Show this help message and exit
        -v      Show error messages such as recursive dependencies
        -r      Show reverse dependencies, i.e. packages dependent on package
        -f      Flat output instead of default tree output
        -d <depth>      Maximum depth to follow dependencies, default and max is 10
        -s      Show child package dependencies that are already listed
                as direct parent dependencies.
        -n      Remove host(native) dependencies

        Provide a package name from the generated pn-depends.dot file.
        Run the program without a package name to get a list of
        available package names.



#####  Generating Data

The oey.py script uses the dependency tree that bitbake generates with
the `--graphviz` or `-g` option. 

You can generate a dependency list for a particular package or a whole image
at once. This doesn't take long even for an image recipe.

        ~/poky/build$ bitbake -g core-image-minimal


The following files will be generated in the *build* directory.

* task-depends.dot
* pn-buildlist

The `oey.py` script uses `task-depends.dot`
for its data.

The script is hard-coded to look for the data file in the current
working directory so you should run it from the directory where
`*.dot` file is located.


#####  Example

    chbae@yocto:~/poky/build$ oey.py -d 2 openssl

    Package [ openssl ] depends on
         gcc-cross-x86_64
                 autoconf-native
                 automake-native
                 binutils-cross-x86_64
                 flex-native
                 gmp-native
                 libmpc-native
                 libtool-native
                 linux-libc-headers
                 mpfr-native
                 texinfo-dummy-native
                 zlib-native
         gcc-runtime
                 autoconf-native
                 automake-native
                 libgcc
                 libtool-native
                 texinfo-dummy-native
         glibc
                 autoconf-native
                 automake-native
                 bison-native
                 gperf-native
                 libgcc-initial
                 libtool-native
                 linux-libc-headers
                 make-native
                 texinfo-dummy-native
         opkg-utils
         perl-native
                 gdbm-native
                 perlcross-native
                 zlib-native
         pseudo-native
                 attr-native
                 pkgconfig-native
                 sqlite3-native


    chbae@yocto:~/poky/build$ oey.py -r openssl

    Package [ openssl ] is needed by
         curl
                 elfutils
                         binutils
                         iproute2
                 libmicrohttpd
                         elfutils
                                 binutils
                                 iproute2
         python3
                 btrfs-tools
                 libxml2
                         shared-mime-info
         socat
