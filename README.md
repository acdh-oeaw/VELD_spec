# VELD spec

specification of the VELD metadata schema.

## velds

### data veld

```
x-veld:
  data:
    file_type: <FILE_TYPE>
    path: [<PATH>]
    [description: <DESCRIPTION>]
    [contents: <CONTENT>]
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
    file_types: txt
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
    [environment: {<ENVIRONMENT>}]
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
```

### \<ENVIRONMENT>

example:
```
```

### \<FILE_TYPE>
```
<FILE_TYPE> ::= <PRIMITIVE>
```

example:
```
file_type: txt
```

### \<INPUT_OR_OUTPUT>

```
<INPUT_OR_OUTPUT> ::=
  volume: <CONTAINER_PATH>
  environment: <ENVIRONMENT_VAR_NAME> | {<ENVIRONMENT_VAR_NAME>}
  description: [<DESCRIPTION>] 
  file_type: <FILE_TYPE> | {<FILE_TYPE>}
  contents: <CONTENT>
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


### \<VELD_SERVICE_NAME>
```
<VELD_SERVICE_NAME> ::= <PRIMITIVE>
```
example:
```
```

### \<VOLUME>
```
<VOLUME> ::= <HOST_PATH>: <CONTAINER_PATH>
```

### \<PRIMITIVE>
Any primitve data type, i.e. not a list or a dictionariy.
example:
```
this is a string
```
```
42
```

