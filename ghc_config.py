extlinks = {
    'ghc-ticket': ('https://gitlab.haskell.org/ghc/ghc/issues/%s', '#'),
    'ghc-wiki': ('https://gitlab.haskell.org/ghc/ghc/wikis/%s', '#'),
}

libs_base_uri = '../libraries'

# N.B. If you add a package to this list be sure to also add a corresponding
# LIBRARY_VERSION macro call to configure.ac.
lib_versions = {
    'base': '4.17.0.0',
    'ghc-prim': '0.9.0',
    'template-haskell': '2.19.0.0',
    'ghc-compact': '0.1.0.0',
    'ghc': '9.4.4',
    'parallel': '@LIBRARY_parallel_VERSION@',
    'Cabal': '3.8.1.0',
    'array': '0.5.4.0',
}

version = '9.4.4'

llvm_version_min = '10'
llvm_version_max = '14'
