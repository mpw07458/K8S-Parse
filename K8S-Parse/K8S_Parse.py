class K8S_Parse(object)

    def __init__(self, data):
    pass

def k8s_yaml_to_dict_helper(yaml_file_name):
    """
    Create a dictionary from a yaml file
    :param yaml_file_name:
    :return:
    """
    # if os.name == 'nt':
    # temp_dir_name = 'c:\\temp\\'
    # else:
    temp_dir_name = '__main__'
    with open(os.path.join(os.path.dirname(temp_dir_name), yaml_file_name)) as f:
        data_loaded = yaml.load(f)
    pprint(data_loaded)
    return data_loaded


def split_yaml_file(self, app_name, app_yaml_file_url, app_svc_name, app_namespace):
    logging.debug("In Init, Calling routine: " + sys._getframe().f_back.f_code.co_name)
    base = app_name
    vol_yaml_file_name = base + '-volume.yaml'
    svc_yaml_file_name = base + '-service.yaml'
    deploy_yaml_file_name = base + '-deploy.yaml'

    f = urlopen(app_yaml_file_url)
    for key, group in it.groupby(f, lambda line: line.startswith('---')):
        if not key:
            group = list(group)
            if any('Deployment' in s for s in group):
                with open(deploy_yaml_file_name, 'w') as de:
                    for item in group:
                        self._hasDeploy = True
                        de.write("%s" % item)
                    de.close()
            elif any('Service' in s for s in group):
                with open(svc_yaml_file_name, 'w') as sv:
                    for item in group:
                        self._hasService = True
                        sv.write("%s" % item)
                    sv.close()
            elif any('PersistentVolumeClaim'in s for s in group):
                with open(vol_yaml_file_name, 'w') as vc:
                    for item in group:
                        self._hasVolume = True
                        vc.write("%s" % item)
                    vc.close()

    if os.path.isfile(vol_yaml_file_name):
        create_persistent_volume(self, self.core_api_instance, vol_yaml_file_name, app_namespace)
    create_deployment_file(self, self.extensions_v1beta1, deploy_yaml_file_name, app_namespace)
    if os.path.isfile(svc_yaml_file_name):
        create_svc_file(self, self.core_api_instance, svc_yaml_file_name, app_namespace)
        self._current_status = Status.InProgress
        self._current_resource = Resource.K8SObject
        self._current_status_msg = 'Performing Health Check...'
        svc_endp_list = get_svc_endpoints(self, app_namespace, app_svc_name)
        self.svc_obj = get_addr_port_list(svc_endp_list, app_svc_name)
        self.pod_obj = get_pod_object(self, app_name)
        self.secret_obj = get_secrets_list_for_deployment(self, app_name)
        self.volume_obj = get_volume_list_for_deployment(self, app_name)
        self._current_status = Status.Initializing
        self._current_resource = Resource.K8SObject
        self._current_status_msg = 'Completing Health Check...'
        self._status_obj = self._get_current_status(self.svc_obj, self.pod_obj, self.secret_obj, self.volume_obj)
        return {"Status": self._status_obj, "Pods": self.pod_obj, "Endpoints": self.svc_obj, "Secrets": self.secret_obj,
                "Volumes": self.volume_obj}
    pass


def k8s_dict_to_yaml_helper(data_dict, yaml_file_name):
    """
    Helper file to create YAML file from dictionary
    :param data_dict:
    :param yaml_file_name:
    :return:
    """
    with io.open(yaml_file_name, 'w', encoding='utf8') as outfile:
        yaml.dump(data_dict, outfile, default_flow_style=False, allow_unicode=True)
    pass
