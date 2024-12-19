
This package contains the validator for the VELD metadata schema. 

For the specification of the schema, see here: https://github.com/acdh-oeaw/VELD_spec

### how to use the validator

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