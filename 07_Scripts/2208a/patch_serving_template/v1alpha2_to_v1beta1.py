#!/usr/bin/python3

import os
import re
import sys
import argparse
import ruamel.yaml as ryaml
from collections import Counter

def yaml_escape_modification(yamldata):
        
    p = re.findall(r"(?<!\")(\{\{.*\}\}[a-zA-Z0-9\.:\-_/]*)(?!\")", yamldata) 
    c = Counter(p)
    if p is not None:
        for n, v in c.items():
            if "\\n" in n:
                continue
            pattern = n
            yamldata = yamldata.replace(pattern, "\"" + n + "\"")
        return (yamldata, c)
    return (readyaml, None)

def get_yaml_from(filename):
    try:
        with open(filename, 'r') as fd:
            readyaml = fd.read()
            readyaml, c = yaml_escape_modification(readyaml)
            return (ryaml.round_trip_load(readyaml, preserve_quotes=True), c)
    except:
        print("Error: The content is not conforming yaml syntax. %s " % os.path.basename(filename))
        sys.exit(1)

def write_yaml(filename, yaml_data, changes):
    readyaml = ryaml.round_trip_dump(yaml_data, explicit_start=True, default_flow_style=False)
    if changes is not None:
        for n,v in changes.items():
            if "\\n" in n:
                continue
            pattern = "\"" + n + "\""
            readyaml = readyaml.replace(pattern, n)
            pattern = "'" + n + "'"
            readyaml = readyaml.replace(pattern, n)

    with open(filename, "w+") as fd:
        fd.write(readyaml)
    print("Modification Complete: %s" % filename)

# This function only needs to modify the apiVersion as the validation checks for every other things
def edit_st_v1beta1_spec(args, yaml_data):
    # Set the apiVersion
    yaml_data['spec']['template']['apiVersion'] = "serving.kserve.io/v1beta1"
    return yaml_data

def convert_st_v1alpha2_spec(args, yaml_data):
    # Set the apiVersion
    yaml_data['spec']['template']['apiVersion'] = "serving.kserve.io/v1beta1"

    
    specs = yaml_data['spec']['template'].get('spec') 
    #yaml_specs = yaml.load(specs, Loader=yaml.loader.SafeLoader)
    yaml_specs = ryaml.round_trip_load(specs, preserve_quotes=True)
    new_specs = { }

    for akey in yaml_specs['default'].keys():
        new_specs[akey] = {}
        for bkey in yaml_specs['default'][akey].keys():
            if bkey == 'custom': 
                new_specs[akey]['containers'] = [yaml_specs['default'][akey]['custom']['container']]
                if yaml_specs['default'][akey]['custom']['container']['name'] == "kfserving-container":
                    new_specs[akey]['containers'][0]['name'] = "kserve-container"
                new_specs[akey]['imagePullSecrets'] = yaml_data['spec']['imagePullSecrets']
            else:
                new_specs[akey][bkey] = yaml_specs['default'][akey][bkey]

    yaml_data['spec']['template']['spec'] = ryaml.round_trip_dump(new_specs, default_flow_style=False)
    return yaml_data


def remove_serving_template_runtime(yaml_data):

    if yaml_data['metadata'].get('uid'):
        del yaml_data['metadata']['uid']

    if yaml_data['metadata']['annotations'].get('kubectl.kubernetes.io/last-applied-configuration'):
        del yaml_data['metadata']['annotations']['kubectl.kubernetes.io/last-applied-configuration']

    if yaml_data['metadata'].get('resourceVersion'):
        del yaml_data['metadata']['resourceVersion']

    if yaml_data['metadata'].get('creationTimestamp'):
        del yaml_data['metadata']['creationTimestamp']

    if yaml_data.get('status'):
        del yaml_data['status']

    return yaml_data

def is_serving_template_spec(yaml_data):
    if yaml_data['apiVersion'] != "ai.sap.com/v1alpha1":
        print("Error: [Code 0] Not ServingTemplate")
        sys.exit(1)

    if yaml_data['kind'] != "ServingTemplate":
        print("Error: [Code 1] Not ServingTemplate")
        sys.exit(1)


    if yaml_data['metadata'].get('labels') is None:
        print("Error: [Code 2] Not ServingTemplate")
        sys.exit(1)

    if yaml_data['metadata']['labels'].get('scenarios.ai.sap.com/id') is None:
        print("Error: [Code 3] Not ServingTemplate")
        sys.exit(1)

    if yaml_data['spec'].get('template') is None:
        print("Error: [Code 4] Not ServingTemplate")
        sys.exit(1)

def is_v1beta1_spec(yaml_data):
    ret = False
    if yaml_data['spec']['template'].get('apiVersion') is not None and yaml_data['spec']['template']['apiVersion'].endswith("v1beta1"):
        print("Info: v1beta1 apiVersion")
        ret = True

    if yaml_data['spec']['template'].get('spec') is None:
        print("Error: [Code 6] Not ServingTemplate")
        sys.exit(1)

    yaml = ryaml.YAML()
    specs = yaml_data['spec']['template'].get('spec') 
    #yaml_specs = yaml.load(specs, Loader=yaml.loader.SafeLoader)
    yaml_specs = ryaml.round_trip_load(specs, preserve_quotes=True)

    # Don't need to verify the detail spec of the yaml file when is not v1beta1
    if ret == False:
        return ret

    # Specifiy spec for v1beta1 checks
    if yaml_specs.get('predictor') is None:
        print("Error: [Code 7] Not ServingTemplate")
        sys.exit(1)

    kserve_specs = ['tensorflow', 'pmml', 'sklearn', 'lightgbm', 'pytorch', 'triton', 'containers']
    result = Counter([ True if key in kserve_specs else False for key in yaml_specs['predictor'].keys() ])
    if result.get(True) is None:
        print("Error: [Code 8] Not ServingTemplate")
        sys.exit(1)

    if "containers" in yaml_specs['predictor'].keys():
        if yaml_specs['predictor'].get('containers') is not None and len(yaml_specs['predictor']['containers']) == 0:
            print("Error: [Code 9] Not ServingTemplate")
            sys.exit(1)
        elif yaml_specs['predictor'].get('containers') is not None and yaml_specs['predictor'].get('imagePullSecrets') is None:
            print("Error: [Code 9.1] Not ServingTemplate")
            sys.exit(1)
        else:
            for item in yaml_specs['predictor']['containers']:
                if item.get('name') is None or item['name'] not in ["kserve-container", "kfserving-container"]:
                    print("Error: [Code 10] Not ServingTemplate")
                    sys.exit(1)

    # If everything is good we exit. There is nothing for us to do
    if yaml_data['spec']['template']['apiVersion'].startswith("serving.kserve.io"):
        print("Info: Valid ServingTempalte with Kserve v1beta1 spec") 
        sys.exit(0)

    # Needs to overwrite the template's apiVersion
    return ret

def is_v1alpha2_spec(yaml_data):
    if yaml_data['spec']['template'].get('apiVersion') is not None and yaml_data['spec']['template']['apiVersion'].endswith("v1alpha2"):
        print("Info: v1alpha2 apiVersion")
    else:
        print("Info: No apiVersion found")


    yaml = ryaml.YAML()
    specs = yaml_data['spec']['template'].get('spec') 
    #yaml_specs = yaml.load(specs, Loader=yaml.loader.SafeLoader)
    yaml_specs = ryaml.round_trip_load(specs, preserve_quotes=True)

    if yaml_specs.get('default') is None:
        print("Error: [Code 11] Not ServingTemplate")
        sys.exit(1)

    if yaml_specs['default'].get('predictor') is None:
        print("Error: [Code 12] Not ServingTemplate")
        sys.exit(1)

    kf_specs = ['tensorflow', 'pmml', 'sklearn', 'lightgbm', 'pytorch', 'triton', 'custom']
    result = Counter([ True if key in kf_specs else False for key in yaml_specs['default']['predictor'].keys() ])
    if result.get(True) is None:
        print("Error: [Code 13] Not ServingTemplate")
        sys.exit(1)


    if yaml_specs['default']['predictor'].get('custom') is not None and yaml_specs['default']['predictor']['custom'].get('container') is not None: 
        if yaml_specs['default']['predictor']['custom']['container'].get('name') is None or yaml_specs['default']['predictor']['custom']['container']['name'] != "kfserving-container":
            print("Error: [Code 14] Not ServingTemplate")
            sys.exit(1)
        elif yaml_data['spec'].get('imagePullSecrets') is None:
            print("Error: [Code 15] Not ServingTemplate")
            sys.exit(1)

    print("Info: Valid ServingTempalte with kfserving v1alpha2 spec") 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("yaml_filename", type=str, help="ServingTemplate Yaml")
    exclusive_parser = parser.add_mutually_exclusive_group()
    exclusive_parser.add_argument('-i', dest="inplace", action='store_true', help="Inplace yaml update")
    exclusive_parser.add_argument('-t', "--test", dest="test", action='store_true', help="Test the yaml file need modification")

    args = parser.parse_args()

    filename = os.path.realpath(args.yaml_filename)
    if not os.path.isfile(filename) or not os.path.exists(filename):
        print("Error: {0} is not a file.".format(args.yaml_filename))
        sys.exit(1)

    # Due to the use of {{...}} there is a need to filter them in sub_groups
    # and sub them as "{{...}}" before we process them
    yaml_data, sub_groups = get_yaml_from(filename) 

    # if is not a servingtemplate it will just quit
    is_serving_template_spec(yaml_data)

    # if is a servingtemplate v1beta1, but apiVersion is incorrect.
    # if is a perfect servingtemplate v1beta1 we exit with a smile in the function.
    if is_v1beta1_spec(yaml_data):
        yaml_data = edit_st_v1beta1_spec(args, yaml_data)    
    else:
        is_v1alpha2_spec(yaml_data)
        yaml_data = convert_st_v1alpha2_spec(args, yaml_data)    

    # Remove any unnecessary annotation in the template
    yaml_data = remove_serving_template_runtime(yaml_data)

    if args.test:
        sys.exit(0)

    if not args.inplace:
        filename = os.path.splitext(filename)[0] + ".mod.yaml"
    write_yaml(filename, yaml_data, sub_groups)
        

if __name__ == "__main__":
    main()
