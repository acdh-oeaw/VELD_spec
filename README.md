# VELD spec

**version v1.0**

This is the formal specification of the VELD metadata schema.

The technical concept of the VELD architecture design can be found
here: https://zenodo.org/records/13322913

**table of contents:**

- [pip installable validator](#pip-installable-validator)
- [Primer on yaml+BNF metasyntax of the specification](#primer-on-yamlbnf-metasyntax-of-the-specification)
  - [non-variable](#non-variable)
  - [variable](#variable)
  - [optional](#optional)
  - [list](#list)
  - [disjunction](#disjunction)
  - [composition](#composition)
- [VELD specification](#VELD-specification)
  - [data veld](#data-veld)
  - [code veld](#code-veld)
  - [chain veld](#chain-veld)
  - [VELD variables](#veld-variables)

## pip installable validator

This repo also contains code for the validator which can be installed via pip with:

```
pip install veld-spec
```

import with:

```
from veld_spec import validate
```

Use it to validate veld yaml files, either by passing the content as python dictionary or by passing
the name of a yaml file:

```
validate(dict_to_validate={"x-veld": {...}})
```

```
validate(yaml_to_validate="veld_file.yaml")
```

It will return a tuple which:

- if the veld yaml content is valid, the first element is `True` and the second `None`

```
(True, None)
```

- if the veld yaml content is invalid, the first element is `False` and the second contains the
  error message.

```
(False, 'root node x-veld missing')
```

## Primer on yaml+BNF metasyntax of the specification

This section is a primer on how to read the metasyntax of the VELD specification, which is expressed
in yaml syntax with [BNF-like metasyntax](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form).
Any yaml file adhering to this schema becomes a valid representation of a VELD object.

This is the exhaustive list of compoments that make up the VELD specification:

- [non-variable](#non-variable)
- [variable](#variable)
- [optional](#optional)
- [list](#list)
- [disjunction](#disjunction)
- [composition](#composition)

### non-variable

Anything that is not a variable or marked with special syntax as described below must exist as-is.

Example:

A yaml file adhering to the schema must have a [mapping](https://yaml.org/spec/1.2.2/#nodes) at the
root named `root` containing a child mapping `sub` which must be empty

```
root:
  sub:
```

valid:

is identical to the simple schema above.

```
root:
  sub:
```

invalid:

is missing the mapping `sub`

```
root:
```

invalid:

contains a non-defined additional element `root_2`

```
root:
  sub:
root_2:
```

### variable

Variables are marked with `<` and `>` and defined with `::=`. They may nest other variables but must
ultimately resolve to a basic [yaml scalar](https://yaml.org/spec/1.2.2/#scalars).

Example:

In this yaml content, a variable `<SOME_VALUE>` is used as a placeholder, indicating that it can be
replaced with any content that fits its definition somewhere else: `<SOME_VALUE> ::= `, while the
other non-variable yaml keys `root` and `sub` need to be present exactly in such structure with
identical naming. (Note that `<SCALAR>` is the only variable not defined within this document as it
refers to the yaml scalar type, defined in [yaml 1.2.2](https://yaml.org/spec/1.2.2/) itself)

variable usage

```
root:
  sub: <SOME_VALUE>
```

variable definition:

The value `<SOME_VALUE>` can be replaced with any yaml scalar, e.g. string, integer, boolean etc.
But no complex type like lists or mappings are allowed.

```
<SOME_VALUE> ::= <SCALAR>
```

valid:

`foo` is a simple yaml scalar

```
root:
  sub: foo 
```

invalid:

`foo` is not a scalar, but a more complex mapping

```
root:
  sub: 
    foo: bar 
```

### optional

Content that is optional is marked with `[` and `]`. Inside can be any other components or 
compositions. If a collection of yaml objects is marked as optional, it must be either absent or
present fully; partial objects are invalid.

Example:

A single value may be present or not, but the key of its mapping must be present

```
root:
  sub: [<SCALAR>]
```

valid:

optional value does not exist

```
root:
  sub: 
```

valid:

optional value does exist

```
root:
  sub: foo 
```

invalid:

non-optional key of the mapping does not exist

```
root:
```

Example:

An entire mapping is marked as optional

```
root:
  [sub: <SCALAR>]
```

valid:

optional mapping does not exist

```
root:
```

valid:

optional mapping does exist

```
root:
  sub: foo 
```

invalid:

Only the key of the optional mapping exists, but not its value.

```
root:
  sub: 
```

### list

Lists are defined with `{` and `}`. Within can be any content, complex or not, variables or not, and
any nestings of such. A valid list is where all its elements adhere to the definition, and it can be
of any cardinality, including zero.

Example:

The content of the mapping with key `sub` must be a list of simple scalars.

```
root:
  sub: {<SCALAR>}
```

valid:

A list with only scalars

```
root:
  sub:
    - foo
    - bar
```

valid:

No value at all, which can also be interpreted as an empty list

```
root:
  sub:
```

invalid:

A list with a scalar and a mapping

```
root:
  sub:
    - foo
    - bar: baz
```

### disjunction

Indicating a range of possibilities with `|` in between the options, of which precisely one must be
fulfilled.

example:

content of `sub` must be either a single scalar or a list of scalars.

```
root:
  sub: <SCALAR> | {<SCALAR>} 
```

valid:

is a single scalar

```
root:
  sub: foo 
```

valid:

is a list of scalars

```
root:
  sub:
    - foo
    - bar 
```

invalid:

It's neither a scalar nor a list of scalars, but a mapping

```
root:
  sub:
    foo: bar 
```

### composition

Any components described above can be arbitrarily combined and nested.

example:

A root element `root` must exist, containing two mappings. The first mapping with key `sub_1`
must contain a scalar. The second mapping `sub_2` is entirely optional and may contain either a
single scalar or a list of the variable `<SUB_CONTENT>`. The variable `<SUB_CONTENT>` contains two
more mappings, where the key `sub_sub_1` must exist, but its value is optional and references the
variable `<BOOL>` which must be either `true` or `false`. The other mapping
`sub_sub_2` is optional entirely, and it contains a single mapping `sub_sub_sub` to a list of
scalars.

```
root:
  sub_1: <SCALAR> 
  [sub_2: <SCALAR> | {<SUB_CONTENT>}]
```

```
<SUB_CONTENT> ::= 
  sub_sub_1: [<BOOL>]
  [sub_sub_2: 
    sub_sub_sub: {<SCALAR>}
  ] 
```

```
<BOOL> ::= true | false
```

valid:

```
root:
  sub_1: foo
```

valid:

```
root:
  sub_1: foo
  sub_2: 
    - foo_1
    - foo_2
    - foo_3
```

valid:

```
root:
  sub_1: foo
  sub_2:
    sub_sub_1:
```

valid:

```
root:
  sub_1: foo
  sub_2:
    sub_sub_1: true
    sub_sub_2:
      sub_sub_sub:
        - foo_1
        - foo_2
```

## VELD specification

The following sections contain the specifications for the three VELD objects and their variables:

- [data veld](#data-veld)
- [code veld](#code-veld)
- [chain veld](#chain-veld)
- [VELD variables](#veld-variables)

### data veld

```
x-veld:
  data:
    file_type: <FILE_TYPE>
    [path: <PATH>]
    [description: <DESCRIPTION>]
    [contents: <CONTENT> | {<CONTENT>}]
    [topics: <TOPIC> | {<TOPIC>}] 
    [additional: <ADDITIONAL>]
```

example:

```
x-veld:
  data:
    description: training data for word embeddings
    topics:
      - NLP
      - word embeddings
    file_type: txt
    additional:
      generated_on: 2024-09-15
```

### code veld

```
x-veld:
  code:
    [description: <DESCRIPTION>]
    [topics: <TOPIC> | {<TOPIC>}] 
    [additional: <ADDITIONAL>]
    [inputs: {<INPUT_OR_OUTPUT>}]
    [outputs: {<INPUT_OR_OUTPUT>}]
    [settings: {<SETTING>}]
services:
  <VELD_SERVICE_NAME>:
    <DOCKER_COMPOSE_DEFINITION>
    [volumes: {<VOLUME>}]
    [environment: <ENVIRONMENT>]
```

example:

```
x-veld:
  code:
    description: ""
    topics:
      - ""
    additional:
      foo:
        bar:
    inputs:
      - description: ""
        volume: /veld/input/
        environment: in_file
        file_type: ""
        contents:
          - ""
    outputs:
      - description: ""
        volume: /veld/output/
        environment: out_file
        file_type: ""
        contents:
          - ""
    environment:
      in_file:
        description: ""
      out_file:
        description: ""
      foo:
        description: ""
        env_type: ""
        optional: ""
        default: ""

services:
  veld:
    build: .
    command: python /veld/code/train.py
    volumes:
      - ./src/:/veld/code/:z
      - ./data/in/:/veld/input/:z
      - ./data/out/:/veld/output/:z
    environment:
      in_file: null
      out_file: null
      foo: null
```

### chain veld

```
x-veld:
  chain:
    [description: <DESCRIPTION>]
    [topics: <TOPIC> | {<TOPIC>}] 
    [additional: <ADDITIONAL>]
services:
  <VELD_SERVICE_NAME>:
    extends:
      file: <VELD_CODE_YAML>
      service: <VELD_SERVICE_NAME>
    [volumes: {<VOLUME>}]
    [environment: <ENVIRONMENT>]
```

example:

```
x-veld:
  chain:
    description: ""
    topics:
      - ""
    additional:
      foo:
        bar:

services:
  veld:
    extends:
      file: ./veld_repo/veld_file.yaml
      service: veld
    volumes:
      - ./data/in/:/veld/input/:z
      - ./data/out/:/veld/output/:z
    environment:
      in_file: null
      out_file: null
      foo: null
```

### VELD variables

All the variables referenced above.

#### \<ADDITIONAL>

Any arbitrary non-veld data, expressed as any kind of yaml data (allowing single values, nested
key-values, lists, etc.), which might be necessary for internal use or extending functionality not
covered by VELD.

example:

```
additional:
  modified_on:
    - 2024-02-09
    - 2024-09-15
```

#### \<CONTENT>

```
<CONTENT> ::= <SCALAR>
```

#### \<BOOL>

```
<BOOL> ::= true | false
```

either `true` or `false`

#### \<DESCRIPTION>

```
<DESCRIPTION> ::= <SCALAR>
```

Any kind of textual description, intended for humans. Can be as long or concise as desired.

example:

```
description: training data for word embeddings
```

#### \<DOCKER_COMPOSE_DEFINITION>

example:

```
<DOCKER_COMPOSE_DEFINITION> ::= <SCALAR>
```

#### \<ENVIRONMENT>

```
<ENVIRONMENT> ::= {<ENVIRONMENT_VAR_NAME>: <SCALAR>}
```

example:

```
```

#### \<ENVIRONMENT_VAR_NAME>

```
<ENVIRONMENT_VAR_NAME> ::= <SCALAR>
```

example:

```
```

#### \<ENV_TYPE>

must be one of the following literals:

```
<ENV_TYPE> ::= str | bool | int | float
```

example:

```
```

#### \<FILE_TYPE>

```
<FILE_TYPE> ::= <SCALAR>
```

example:

```
```

example:

```
file_type: txt
```

example:

```
```

#### \<INPUT_OR_OUTPUT>

```
<INPUT_OR_OUTPUT> ::=
  volume: <CONTAINER_PATH>
  [environment: <ENVIRONMENT_VAR_NAME>]
  [description: <DESCRIPTION>] 
  [file_type: <FILE_TYPE> | {<FILE_TYPE>}]
  [contents: <CONTENT> | {<CONTENT>}]
```

example:

```
```

#### \<PATH>

```
<PATH> ::= <SCALAR>
```

example:

```
```

#### \<SCALAR>

Any primitive data type, i.e. not a list or a dictionary. example:

```
this is a string
```

```
42
```

#### \<SETTING>

```
<SETTING> ::= 
  environment: <ENVIRONMENT_VAR_NAME>
  [description: <DESCRIPTION>]
  [env_type: <ENV_TYPE>]
  [default: <SCALAR>]
  [optional: <BOOL>]
```

example:

```
  environment: vector_size
  description: "word2vec hyperparameter: number of dimensions of the word vectors"
  env_type: int
  default: 200
  optional: true
```

#### \<TOPIC>

can be a single value or a list of single values (note that the list must be expressed as yaml list,
i.e. newline and a hyphen)

```
<TOPIC> ::= <SCALAR>
```

example:

```
topics: NLP
```

```
topics: 
  - NLP
  - word embeddings
```

#### \<VELD_CODE_YAML>

```
<VELD_CODE_YAML> ::= <SCALAR>
```

example:

```
```

#### \<VELD_SERVICE_NAME>

```
<VELD_SERVICE_NAME> ::= <SCALAR>
```

example:

```
```

#### \<VOLUME>

```
<VOLUME> ::= <HOST_PATH>:<CONTAINER_PATH>
```

example:

```
```
