# VELD spec

specification of the VELD metadata schema.

TODO:
- veld technical concept
- pip
- notes on notation

## velds

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

## variables

### \<ADDITIONAL>

Any arbitrary non-veld data, expressed as any kind of yaml data (allowing single values, nested 
key-values, lists, etc.), which might be necessary for internal use or extending functionality not covered by VELD.

example:
```
additional:
  modified_on:
    - 2024-02-09
    - 2024-09-15
```

### \<CONTENT>

```
<CONTENT> ::= <PRIMITIVE>
```

### \<BOOL>

either `true` or `false`

### \<DESCRIPTION>

```
<DESCRIPTION> ::= <PRIMITIVE>
```

Any kind of textual description, intended for humans. Can be as long or concise as desired.

example:
```
description: training data for word embeddings
```

### \<DOCKER_COMPOSE_DEFINITION>

example:
```
<DOCKER_COMPOSE_DEFINITION> ::= <PRIMITIVE>
```

### \<ENVIRONMENT>

```
<ENVIRONMENT> ::= {<ENVIRONMENT_VAR_NAME>: <PRIMITIVE>}
```
example:
```
```

### \<ENVIRONMENT_VAR_NAME>

```
<ENVIRONMENT_VAR_NAME> ::= <PRIMITIVE>
```
example:
```
```

### \<ENV_TYPE>

must be one of the following literals:
```
<ENV_TYPE> ::= str | bool | int | float
```
example:
```
```

### \<FILE_TYPE>

```
<FILE_TYPE> ::= <PRIMITIVE>
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

### \<INPUT_OR_OUTPUT>

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

### \<PATH>

```
<PATH> ::= <PRIMITIVE>
```
example:
```
```


### \<PRIMITIVE>

Any primitive data type, i.e. not a list or a dictionary.
example:
```
this is a string
```
```
42
```

### \<SETTING>

```
<SETTING> ::= 
  environment: <ENVIRONMENT_VAR_NAME>
  [description: <DESCRIPTION>]
  [env_type: <ENV_TYPE>]
  [default: <PRIMITIVE>]
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

### \<TOPIC>

can be a single value or a list of single values (note that the list must be expressed as yaml 
list, i.e. newline and a hyphen)
```
<TOPIC> ::= <PRIMITIVE>
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


### \<VELD_CODE_YAML>

```
<VELD_CODE_YAML> ::= <PRIMITIVE>
```
example:
```

### \<VELD_SERVICE_NAME>

```
<VELD_SERVICE_NAME> ::= <PRIMITIVE>
```
example:
```
```

### \<VOLUME>

```
<VOLUME> ::= <HOST_PATH>:<CONTAINER_PATH>
```
example:
```
```
