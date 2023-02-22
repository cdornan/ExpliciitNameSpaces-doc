.. explicit_namespaces documentation master file

Explicit namespaces in import/export lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. extension:: ExplicitNamespaces
    :shortdesc: Enable the use of the keywords ``type`` and ``data`` to specify the precise
        entities exported from a module and brought into scope by an import declaration 
        (:ref:`explicit-namespaces`).

    :implied by: :extension:`TypeOperators`, :extension:`TypeFamilies`
    :since: 7.6.1

    Enable use of explicit namespaces in module import and export lists.

Background
~~~~~~~~~~

Haskell has two namespaces:

* the *type namespace*, including the names of type constructors, type
  synonyms, type families and type classes;

* the *data namespace*, including the names of term-level values, functions,
  data constructors and pattern synonyms.

This separation allows us to define data constructors and type
constructors whose names coincide:

.. code:: haskell

   data T = T

(Similarly, with the ``TypeOperators`` extension it is possible to define
term-level operators and type families whose names coincide.)

At use sites, GHC infers which ``T`` is referred to from the context:

.. code:: haskell

   t :: T  -- type-level T
   t = T   -- term-level T

The use of identical names for type-level and term-level entities is called
*punning*.  Haskell makes heavy use of punning in its built-in syntax and common
types.

However, there are various contexts in which an occurrence of a name may refer
either to the type namespace or the data namespace, and it is not always clear
which is meant. In particular, the following may mention both type-level and
term-level entities:

- Import and export lists

- Fixity declarations

- ``WARNING``, ``DEPRECATED`` and ``ANN`` pragmas

- Types, when using the ``DataKinds`` extension to reference a data constructor
  at the type level

- Template Haskell name quotes

In certain situations, which appear to be geining prevalence in modern Haskell, precison is needed
in specifying exactly which names are exported or imported from a module. This extension aims to
provide precise control in the presence of puns where the same name is present in the type and
data namespace.

ExplicitNamespaces Overview
---------------------------

When the ``ExplicitNamespaces`` extensiopn is enabled, ``type`` and ``data`` keywords may be prefixed
to a qualified constructor names in import and export lists to specify whether a type constructor
or data constructor is being exported or brought into scope.  It is an error to use such a namespace
specifier if the identifier is not in scope in the given namespace.

More precisely, the standard grammar of Haskell import/export items is
essentially the following (after some minor simplifications): ::

      export -> qcname_ext ['(' qcname_ext_w_wildcard_1, ..., qcname_ext_w_wildcard_n ')']
             |  'module' modid

      qcname_ext_w_wildcard -> qcname_ext
                            |  '..'

      qcname_ext -> qvar
                 |  qtycon

This extension extends ``qcname_ext`` as follows: ::

      qcname_ext -> qvar
                 |  qtycon
                 | 'type' oqtycon  -- with ExplicitNamespaces
                 | 'data' qvarcon  -- with ExplicitNamespaces

Notice that:

- ``module`` is valid only at the top level of the export,
  whereas ``type`` and ``data`` are valid either at the top or nested inside a
  type constructor or typeclass name.

- ``data`` may be followed by a data constructor name or a variable name (with
  the latter including record selectors, in particular).


Namespace-specified imports
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the ``ExplicitNamespaces`` extension is enabled, the syntax of import
declarations is extended to include a namespace specifier immediately after the
module identifier.

More concretely, in the grammar accepted by GHC, ::

      importdecl -> 'import' [src] ['safe'] ['qualified'] [package] modid ['qualified'] ['as' modid] [impspec]

is changed to ::

      importdecl -> 'import' [src] ['safe'] ['qualified'] [package] modid [namespace] ['qualified'] ['as' modid] [impspec]

      namespace  -> 'data'
                 |  'type'

With a namespace specified in the import, only identifiers belonging to the
corresponding namespace will be brought into the scope, as if an explicit import
list was given mentioning only those identifiers (with the namespace specifier
on each item).

If an import declaration uses both a namespace specifier and an explicit import
list, the explicit import list may not mention a different namespace specifier,
nor an identifier that is not available in the given namespace, otherwise a name
resolution error will be reported.  It is allowed to redundantly specify the
same namespace specifier on the import declaration and on an individual item.

If an import declaration uses a namespace specifier but no explicit import list,
it is not an error for the declaration to bring no names into scope,
e.g. because the ``data`` specifier was used on a module that exports only type
names. (GHC may of course warn that such an import is redundant.)


Examples
---------


.. code:: haskell

   {-# LANGUAGE ExplicitNamespaces, TypeFamilies #-}
   {-# OPTIONS_GHC -Wpattern-namespace-specifier #-}
   module M
     ( D            -- Accepted: exports data family D
     , data D       -- Accepted: exports data constructor D
     , C(type D)    -- Accepted: exports class C and data family D
     , D(data f)    -- Accepted: exports data family D and field f
     , pattern D    -- Accepted: exports data constructor D but emits warning
     , T(data D)    -- Accepted: exports type T and data constructor D
     , data f       -- Accepted: exports field f
     , data v       -- Accepted: exports term v
     , type T (..)  -- Accepted: exports type T and all its constructors
     , T(pattern D) -- Rejected: pattern keyword cannot be used in sub-list
     , data T       -- Rejected: T not in scope in data namespace
     , type E       -- Rejected: E not in scope in type namespace
     ) where

   class C a where
     data D a

   instance C Int where
     data D Int = E { f :: Int }

   data T = D | D2

   v = ()


.. code:: haskell

   {-# LANGUAGE ExplicitNamespaces #-}
   module M
     ( (+)       -- Accepted: exports value-level function
     , data (+)  -- Accepted: exports value-level function
     , type (+)  -- Accepted: exports type family
     ) where

   import Prelude (data (+))
   import GHC.TypeLits (type (+))


.. code:: haskell

   {-# LANGUAGE ExplicitNamespaces #-}
   module M
     ( type (+++) (data X)  -- Accepted: exports data type (+++) and its constructor
     , (+++) (X)            -- Rejected: variable (+++) cannot have a sub-list
     ) where

   (+++) = (+)

   data a +++ b = X
