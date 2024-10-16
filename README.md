# VELD spec

specification of the VELD metadata schema.

## data veld

```
x-veld:
  data:
    description: <DESCRIPTION>
    topics: <TOPICS> 
    file_types: <FILE_TYPES>
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
## code veld
```
x-veld:
  code:
    description: <DESCRIPTION>
    topics: <TOPICS> 
    [additional: <ADDITIONAL>]
    inputs: <INPUTS>
    outputs: <OUTPUTS>
    environment_vars: <ENVIRONMENT_VARS>

services:
  <VELD_SERVICE_NAME>:
    <DOCKER_COMPOSE_DEFINITION>
    volumes: <VOLUMES>
    environment: <ENVIRONMENT>
```
example:
```
x-veld:
  code:
    description: <TEXTUAL_DESCRIPTION_MEANT_FOR_HUMANS>
    topics: <TOPICS> 
    additional:
      <ARBITRARY_SUB_YAML_DATA>

    inputs: <INPUTS>
    
      - description: ""
        volume: /veld/input/
        environment: in_file
        file_types: ""
        contents:
          - ""

    outputs:
      - description: ""
        volume: /veld/output/
        environment: out_file
        file_types: ""
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

## chain veld
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

### \<DESCRIPTION>

Any kind of textual description, intented for humans. Can be as long or concise as desired.

example:
```
description: training data for word embeddings
```

### \<TOPICS>

can be a single value or a list of single values (note that the list must be expressed as yaml 
list, i.e. newline and a hyphen)
```
<TOPICS>: <SINGLE_TOPIC> | { <SINGLE_TOPIC> }+ 
```
where `<SINGLE_TOPIC>` can be arbitrary textual tags, associating the veld to some broader 
context.  

example:
```
topics: NLP
```
```
topics: 
  - NLP
  - word embeddings
```

### \<ADDITIONAL>

Any arbitrary non-veld data, expressed as any kind of yaml data (allowing single values, nested 
key-values, lists, etc), which might be necessary for internal use or extending functionality not covered by VELD.

example:
```
additional:
  modified_on:
    - 2024-02-09
    - 2024-09-15
```
