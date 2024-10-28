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

Example:

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

Example:

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

Details and reasonings on this design are discussed in greater depth in the Technical Concept found
here: https://zenodo.org/records/13322913

As a very brief introduction, the three VELD objects represents units which are functionally
distinct and atomic, but are composable to form reproducible and adaptable workflows. Each such unit
is manifested as an atomic git repository. **Data velds** are data repositories, **code velds** are
software repositories able to consume and produce data velds, and **chain velds** are the
aggregations of data and code velds. Execution of code velds within chain velds is implemented with
docker compose, and aggregations of data velds with code velds into chain velds is done with git
submodules. Each of these objects is described with respective veld yaml files adhering to the
schema described below.

### data veld

The simplest object is a data veld. It is a repository containing only data, without any code or
software integrated. Its data can be of any kind and VELD does not impose any restrictions down onto
the data. But in order to make the data integrable into the VELD design, it should contain metadata
expressed within a VELD yaml file. The name of the must start with `veld`, and if there are multiple
veld yaml files in the same location their names after `veld_` may be arbitrarily chosen.  
Preferably the VELD yaml file is stored in the same folder as the dataset / file it describes; if
this is not possible it should point to the dataset / file with the `path` settings.

Note that all the variables marked with `<` and `>` are described in their own section
under [VELD variables](#veld-variables).

```
# mandatory: the x-veld tag marks this yaml file as a VELD object
x-veld:

  # mandatory: the next key marks this VELD object as a data veld
  data:
  
    # the file type of the data; the only mandatory element
    file_type: <FILE_TYPE>
    
    # optional: path to the data, relative to the veld yaml file 
    [path: <PATH>]
    
    # optional: any kind of human-oriented description of any length
    [description: <DESCRIPTION>]
    
    # optional, either single value or list: the content within the files
    [contents: <CONTENT> | {<CONTENT>}]
    
    # optional, either single value or list: what broader topics does this touch upon? 
    [topics: <TOPIC> | {<TOPIC>}]
    
    # optional: any kind of non-VELD data in any yaml structure, meant for ad-hoc usage
    [additional: <ADDITIONAL>] 
```

Example:

This data veld yaml describes a single text file with `file_type` of `txt` in which the entire
german wikipedia is stored as expressed in `description`. The `contents` section shows that this
data is raw text.

```
x-veld:
  data:
    file_type: txt
    description: The entire german wikipedia, in a single txt file, where each line is a single 
      sentence
    contents: raw text
```

This data veld yaml describes a fasttext model which is a binary file, epxressed as `file_type:
bin` and touches upon the broader `topics` of `NLP` and exemplifies `word embeddings`. Because there
is no explitict common file type for these kind of data, the fact that it deals with such language
models is communicated within the `contents` section. Additionally, an explicit `path` is defined
since it is assumed, that the model lies in a subfolder relative to the veld data yaml. Also, there
is `additional` data attached that is ignored by the VELD metadata, but might of internal use.

```
x-veld:
  data:
    file_type: bin
    description: self-trained fasttext word embeddings model on wikipedia data
    contents:
      - word embeddings model
      - fasttext model
    path: model_data/m3.bin
    topics:
      - NLP
      - word embeddings
    additional:
      generated_on: 2024-09-15
      by: SteffRhes
```

### code veld

The code veld yaml (and that of chains) are special insofar as they not only describe VELD metadata,
but also are fully
conforming [docker compose files](https://docs.docker.com/reference/compose-file/) (Hence also
the `x-veld` root tag as anything `x-` is ignored by docker). This means that the code veld yaml is
split into two sections: VELD metadata and the docker compose service defintion. VELD does not
impose anything onto the compose service definition, so any code veld yaml will always be able to be
executed by docker alone, independent of VELD. Hence, the following code veld specification will not
detail the service specification but only briefly refers to it.

Note that all the variables marked with `<` and `>` are described in their own section
under [VELD variables](#veld-variables).

```
# mandatory: the x-veld tag marks this yaml file as a VELD object
x-veld:

  # mandatory: the next key marks this VELD object as a code veld
  code:
  
    # optional: any kind of human-oriented description of any length
    [description: <DESCRIPTION>]
    
    # optional, either single value or list: what broader topics does this touch upon? 
    [topics: <TOPIC> | {<TOPIC>}]
    
    # optional: any kind of non-VELD data in any yaml structure, meant for ad-hoc usage
    [additional: <ADDITIONAL>]   
  
    # optional: describes the various inputs this code veld can consume 
    [inputs: {<INPUT_OR_OUTPUT>}]
    
    # optional: describes the various outputs this code veld can produce
    [outputs: {<INPUT_OR_OUTPUT>}]
    
    # optional: describes the various settings that can modify the code veld's behavior
    [settings: {<SETTING>}]
    
# mandatory: docker compose service section
services:

  # mandatory: name of the compose service, naming it either or prefixing it `veld` is recommended 
  <VELD_SERVICE_NAME>:
  
    # mandatory: any kind of compose service definition, necessary for functionality
    <DOCKER_COMPOSE_DEFINITION>
    
    # optional: offering volume mounts for standalone non-VELD usage of the code veld 
    [volumes: {<VOLUME>}]
    
    # optional: environment variables, which might be necessary and or referenced by other parts 
    [environment: <ENVIRONMENT>]
```

Example:

This is a code veld that downloads an entire wikipedia dump, defined with the
variable `wikipedia_dump_url`, extracts the compressed data and stores it as `json` files in a
folder, specified in the `outputs` section. Note that in that same section, `file_type` and
`contents` are also described, which is an overlap to the data veld's sections, enabling potential
interoperability.

```
x-veld:
  code:
    description: "downloading wikipedia archive and extracting each article to a json file."
    topics:
      - "NLP"
      - "Machine Learning"
      - "ETL"

    outputs:
      - volume: /veld/output/
        description: "a folder containing json files, where each file contains the contents of a
          wikipedia article"
        file_type: "json"
        contents: 
          - "NLP training data"
          - "raw text"

    settings:
      - environment: wikipedia_dump_url
        description: "url to a wikipdedia dump download, from https://dumps.wikimedia.org/"
        env_type: "str"
      - environment: out_data_description
        description: "short human description for the data and its purpose, will be persisted in a
          data veld yaml"
        env_type: "str"
        optional: true
      

services:
  veld_download_and_extract:
    build: .
    volumes:
      - ./src/:/veld/code/:z
      - ./data/wikipedia_json/:/veld/output/:z
    command: /veld/code/download_and_extract.sh
    environment:
      wikipedia_dump_url: null
      out_data_description: null
```

The following code veld takes the json files produced by the previous example as input (mounted to
docker container internal path `/veld/input/` and `in_json_folder`)
and aggregates their content into a single txt file (mounted to container path `/veld/output/` and a
name provided by the environment variable `out_txt_file`), with each line either being a sentence (
done by SpaCy's sentence split) or an entire article depending on the setting
`set_split_sentences`. Additionally, there are various ETL specific settings such as `cpu_count`
which allocates the number of CPU cores for this service, `sample_size_percentage` which sets the
percentage of potential sample data to be generated, `sample_random_seed` setting a reproducible
randomness seed, `buffer_segments` which defines the segments in between which data is persisted
into temporary checkpoints, should the preprocessing crash and continue from a safe state.

```
x-veld:
  code:
    description: "transforming wikipedia raw jsons to a single txt file."
    topics:
      - "NLP"
      - "Machine Learning"
      - "ETL"

    inputs:
      - volume: /veld/input/
        description: "a folder containing json files, where each file contains the contents of a
          wikipedia article"
        environment: in_json_folder
        file_type: "json"
        contents:
          - "NLP training data"
          - "raw text"

    outputs:
      - volume: /veld/output/
        description: "single txt file, containing only raw content of wikipedia pagaes, split into 
            sentences or per article with a newline each, possibly being only a sampled subset for 
            testing."
        environment: out_txt_file
        file_type: "txt"
        contents:
          - "NLP training data"
          - "raw text"

    settings:
      - environment: out_data_description
        description: "short human description for the data and its purpose, will be persisted in a
          data veld yaml"
        env_type: "str"
        optional: true
      - environment: cpu_count
        description: "number of cpu cores to be used for parallel processing"
        env_type: "int"
        optional: true
        default: "maximum number of available cpu cores"
      - environment: set_split_sentences
        description: "Should the resulting txt be split by newlines at each sentence boundary? If 
          not, then newlines will be set at the end of each article."
        env_type: "boolean"
        optional: true
        default: false
      - environment: sample_size_percentage
        description: "As percentage, can be used to transform only a sample of the data, for 
          testing purpose most likely. The sample is randomly picked, and a random seed can also 
         be set with `sample_random_seed`"
        env_type: "float"
        optional: true
        default: 100
      - environment: sample_random_seed
        description: "a random seed in case a random sample is drawn and its randomness should be 
          fixed."
        env_type: "str"
        optional: true
        default: null
      - environment: buffer_segments
        description: "The interval at which progress should be printed. E.g. 100 means to print 
          hundred times during processing."
        env_type: "int"
        optional: true 
        default: 100

services:
  veld_transform_wiki_json_to_txt:
    build: .
    volumes:
      - ./src/:/veld/code/:z
      - ./data/wikipedia_json/:/veld/input/
      - ./data/wikipedia_txt/:/veld/output/
    command: python /veld/code/transform_wiki_json_to_txt.py
    environment:
      in_json_folder: null
      out_txt_file: null
      out_data_description: null
      cpu_count: null
      set_split_sentences: false
      sample_size_percentage: 100
      sample_random_seed: null
      buffer_segments: 100
```

### chain veld

Similarly to code velds, the chain veld yamls are also valid docker compose files. They are also
much less descriptive usually than data or code velds as the chains represent the aggregations of
data and code velds and hence are mostly defined implicitly by them anyway with little to no
possibility to depart from their intended usages. The metadata of a chain hence is simplistic and
contains only three elements, of which two are VELD specific. However, within the docker compose
service definition, a chain veld would inherit from a code veld by utilizing docker
compose's [extends functionality](https://docs.docker.
com/compose/how-tos/multiple-compose-files/extends/). And within the `volumes` section the chain
veld would preferably use a data veld's path as input or output. Under the section `environment`
all environment variables must be set as declared by the code veld, which is either file names or
settings.

```
# mandatory: the x-veld tag marks this yaml file as a VELD object
x-veld:

  # mandatory: the next key marks this VELD object as a chain veld
  chain:
    
    # optional: any kind of human-oriented description of any length
    [description: <DESCRIPTION>]
    
    # optional, either single value or list: what broader topics does this touch upon? 
    [topics: <TOPIC> | {<TOPIC>}]
    
    # optional: any kind of non-VELD data in any yaml structure, meant for ad-hoc usage
    [additional: <ADDITIONAL>]
    
# mandatory: docker compose service section
services:

  # mandatory: name of the compose service, naming it either or prefixing it `veld` is recommended 
  <VELD_SERVICE_NAME>:
  
    # mandatory: using `extends` to inherit from a code veld
    extends:
    
      # mandatory: the code veld yaml file 
      file: <VELD_CODE_YAML>
      
      # mandatory: the service name within that code veld yaml
      service: <VELD_SERVICE_NAME>
      
    # optional: volumes where host data is mounted into the code veld container 
    [volumes: {<VOLUME>}]
    
    # optional: environment variables and their values to be passed into the code veld container
    [environment: <ENVIRONMENT>]
```

Example:

This chain uses the previously defined wikipedia downloader code veld, as expressed in the
`extends` section where the local folder (a git
submodule: `veld_code_20_wikipedia_nlp_preprocessing`) and its file
(`veld_download_and_extract.yaml`) and service name of the code veld are
referenced (`veld_download_and_extract`). Within the `volumes` section this chain defines the output
of the code to be stored in a folder `data_local/training_data/extracted/`, and in the
`environment` section the variable `wikipedia_dump_url` is defined, pointing to the wikipedia dump
url where the code veld should download from.

```
x-veld:
  chain:
    description: "downloading wikipedia archive and extracting each article to a json file."
    topics:
      - NLP
      - ETL

services:
  veld_preprocess_download_and_extract:
    extends:
      file: ./veld_code_20_wikipedia_nlp_preprocessing/veld_download_and_extract.yaml
      service: veld_download_and_extract
    volumes:
      - ./data_local/training_data/extracted/:/veld/output/
    environment:
      wikipedia_dump_url: https://dumps.wikimedia.org/dewiki/latest/dewiki-latest-pages-articles.xml.bz2
```

This chain uses the second code veld exemplified above, and takes the output of the previous chain
and uses it as input (in `volumes` expressed as the docker host-container
mapping: `./data_local/training_data/extracted/:/veld/input/`) and produces a new output (with
mapping `./data_local/training_data/extracted__txt_sentence_per_line /:/veld/output/` and file
name `out_txt_file: "de_wiki_sample.txt"`). Note that the resulting txt is split into sentences each
with their own line, set by `set_split_sentences: true` and described in the code veld above
under `settings`. Equally, there are the settings `cpu_count: 14` allocating 14 CPU cores to this
task, and `buffer_segments: 10`, setting the code veld to save its state in 10 intermediate steps.

```
x-veld:
  chain:
    description: "transforming wikipedia raw jsons to a single txt file."
    topics:
      - NLP
      - ETL

services:
  veld_preprocess_transform_wiki_json_to_txt:
    extends:
      file: ./veld_code_20_wikipedia_nlp_preprocessing/veld_transform_wiki_json_to_txt.yaml
      service: veld_transform_wiki_json_to_txt
    volumes:
      - ./data_local/training_data/extracted/:/veld/input/
      - ./data_local/training_data/extracted__txt_sentence_per_line/:/veld/output/
    environment:
      in_json_folder: "data"
      out_txt_file: "de_wiki_sample.txt"
      set_split_sentences: true
      cpu_count: 14
      buffer_segments: 100
```

### VELD variables

All the variables referenced above.

#### \<ADDITIONAL>

Any arbitrary non-veld data, expressed as any kind of yaml data (allowing single values, nested
key-values, lists, etc.), which might be necessary for internal use or extending functionality not
covered by VELD.

Example:

```
additional:
  generated_on: 2024-09-15
  by: SteffRhes
```

#### \<CONTENT>

The content within files / data sets, which is different to `file_type`, since `contents` is
understood as the broader description of the data contrasting the serialization and formatting
expressed by `file_type`

```
<CONTENT> ::= <SCALAR>
```

Example:

```
x-veld:
  data:
    contents: raw text
```

```
x-veld:
  code:
    ... 
    outputs:
        ...
        contents:
          - "NLP training data" # <CONTENT>
          - "raw text" # <CONTENT>
```

#### \<BOOL>

A boolean flag, that can only take the yaml data type of `true` or `false`.

```
<BOOL> ::= true | false
```

Example:

```
x-veld:
  code:
    ...
    settings:
      - environment: out_data_description
        env_type: "str"
        optional: true # <BOOL>
```

#### \<DESCRIPTION>

Any kind of textual description, intended for humans. Can be as long or concise as desired.

```
<DESCRIPTION> ::= <SCALAR>
```

Example:

```
x-veld:
  data:
    ...
    description: The entire german wikipedia, in a single txt file, where each line is a single 
```

#### \<DOCKER_COMPOSE_DEFINITION>

One of two variables not explicitly defined (the other being `<SCALAR>`) within this document as it
refers to the external schema
of [docker compose specification](https://docs.docker.com/reference/compose-file/).

Example:

```
build: .
command: jupyter notebook --allow-root --ip='*' --NotebookApp.token='' --NotebookApp.password=''
ports:
 - 8888:8888
```

#### \<ENVIRONMENT>

While `<ENVIRONMENT>` is also defined with the [docker compose specification](https://docs.docker.
com/reference/compose-file/), it still is explicitly defined here as a part of it shares an 
overlap with other VELD sections, namely `<ENVIRONMENT_VAR_NAME>`, which is referenced in 
`<INPUT_OR_OUTPUT>` and `<SETTING>`.

```
<ENVIRONMENT> ::= {<ENVIRONMENT_VAR_NAME>: <SCALAR>}
```

Example:

```
x-veld:
  code:
    environment: # <ENVIRONMENT> 
      wikipedia_dump_url: null # acting as placeholder
```
```
x-veld:
  chain:
    environment: # <ENVIRONMENT> 
      out_txt_file: "de_wiki_sample.txt" # being assigned a value
      set_split_sentences: true # being assigned a value
```

#### \<ENVIRONMENT_VAR_NAME>

The name of an environment variable. The value is set within the `environment` section and it is 
referenced in `<INPUT_OR_OUTPUT>` and `<SETTING>`

```
<ENVIRONMENT_VAR_NAME> ::= <SCALAR>
```

Example:

```
# in the first code veld there is such a setting defined: 
settings:
  - environment: wikipedia_dump_url # <ENVIRONMENT_VAR_NAME> is wikipedia_dump_url, referencing the variable
    description: "url to a wikipdedia dump download, from https://dumps.wikimedia.org/"
    env_type: "str"
    
# in the first chain veld, the <ENVIRONMENT_VAR_NAME>' is assigned a value withit `environment`
environment:
   # <ENVIRONMENT_VAR_NAME> is wikipedia_dump_url, assigning a value
  wikipedia_dump_url: https://dumps.wikimedia.org/dewiki/latest/dewiki-latest-pages-articles.xml.bz2
```

```
# in the second code veld there is such a output defined: 
- volume: /veld/output/
  environment: out_txt_file # <ENVIRONMENT_VAR_NAME> is out_txt_file, referencing the variable
  file_type: "txt"
  
# in the second chain veld, the <ENVIRONMENT_VAR_NAME>' is assigned a value withit `environment`
environment:
  out_txt_file: "de_wiki_sample.txt" # <ENVIRONMENT_VAR_NAME> is out_txt_file, assigning a value
```

#### \<ENV_TYPE>

If an environment variable is defined within the `settings` section of a code veld, it should be 
assigned a type as well, and can be one of the following literals:

```
<ENV_TYPE> ::= str | bool | int | float
```

Example:

```
x-veld:
  code:
    settings:
      - environment: cpu_count
        env_type: "int" # <ENV_TYPE>
      - environment: set_split_sentences
        env_type: "boolean" # <ENV_TYPE>
```

#### \<FILE_TYPE>

Expressing the serialization format of some data, must be one of the common MIME types

```
<FILE_TYPE> ::= <SCALAR>
```

Example:

```
x-veld:
  data:
    file_type: "txt" # <FILE_TYPE>
```

```
x-veld:
  code:
    inputs:
      - volume: /veld/input/
        file_type: "json" # <FILE_TYPE>
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

Example:

```
```

#### \<PATH>

```
<PATH> ::= <SCALAR>
```

Example:

```
```

#### \<SCALAR>

Any primitive data type, i.e. not a list or a dictionary.

Example:

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

Example:

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

Example:

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

Example:

```
```

#### \<VELD_SERVICE_NAME>

```
<VELD_SERVICE_NAME> ::= <SCALAR>
```

Example:

```
```

#### \<VOLUME>

```
<VOLUME> ::= <HOST_PATH>:<CONTAINER_PATH>
```

Example:

```
```
