## Patch ServingTemplate

The script patches Serving Template with apiVersion `kubeflow.org/v1alpha2` to `kserve.io/v1beta1`

### Setup
Run the following once and use the python3 virtual environment:

1. Create python3 virtual environment
```sh
$ ./setup.sh
venv: 20220810_0935_env
Collecting ruamel.yaml
  Using cached ruamel.yaml-0.17.21-py3-none-any.whl (109 kB)
Collecting ruamel.yaml.clib>=0.2.6
  Using cached ruamel.yaml.clib-0.2.6-cp310-cp310-macosx_10_9_universal2.whl (149 kB)
Installing collected packages: ruamel.yaml.clib, ruamel.yaml
Successfully installed ruamel.yaml-0.17.21 ruamel.yaml.clib-0.2.6
WARNING: You are using pip version 22.0.4; however, version 22.2.2 is available.
You should consider upgrading via the '/Users/i564554/scripts/20220810_0935_env/bin/python3 -m pip install --upgrade pip' command.

usage: ./setup.sh [python3 env location]

    This script will setup the python3 venv.
    If is not specify a directory will be create for you.

Usage steps after setup.

    1. source 20220810_0935_env/bin/activate

    2. python3 v1alpha2_to_v1beta1.py --help
```

2. Setup 
```sh
$ source 20220810_0935_env/bin/activate
```

3. Run the migration on the yaml
```sh
$ python3 v1alpha2_to_v1beta1.py ./test.yaml

# Above script should create output file names test.mod.yaml with v1beta1 spec
```

### Help information

```sh
$ python3 v1alpha2_to_v1beta1.py --help
usage: v1alpha2_to_v1beta1.py [-h] [-i | -t] yaml_filename

positional arguments:
  yaml_filename  ServingTemplate Yaml

  options:
    -h, --help     show this help message and exit
    -i             Inplace yaml update
    -t, --test     Test the yaml file need modification
```

### Error Code when migration yaml
| Code | Description |
| -- | -- |
| 0 | ServingTemplate's apiVersion is not `ai.sap.com/v1alpha1` |
| 1 | ServingTemplate's kind is not `ServingTemplate` |
| 2 | ServingTemplate's `labels` is not present |
| 3 | ServingTemplate `labels.scenarios.ai.sap.com/id` is not present |
| 4 | ServingTemplate is missing `spec.template` |
| 6 | ServingTemplate is missing `spec.template.spec` |
| 7 | ServingTemplate uses v1beta1 spec, but missing `spec.template.spec.predictor` |
| 8 | ServingTemplate uses v1beta1 spec, undefine predictor content |
| 9 | ServingTemplate uses v1beta1 spec, undefine predictor content |
| 9.1 | ServingTemplate uses v1beta1 spec, imagePullSecrets cannot be found |
| 10 | ServingTemplate uses v1beta1 spec, undefine predictor content |
| 11 | ServingTemplate uses v1alpha2 spec, but missing `spec.template.spec.default` |
| 12 | ServingTemplate uses v1alpha2 spec, undefine predictor content |
| 13 | ServingTemplate uses v1alpha2 spec, undefine predictor content |
| 14 | ServingTemplate uses v1alpha2 spec, undefine predictor content |
| 15 | ServingTemplate uses v1alpha2 spec, `imagePullSecrets` cannot be found |
