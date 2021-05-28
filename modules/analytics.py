import oci

resource_name = 'analytics instances'

def c(config, signer, compartments):
    target_resources = []

    print("\nListing all {}... (* is marked for stop)".format(resource_name))
    for compartment in compartments:
        # print("  compartment: {}".format(compartment.name))
        resources = _get_resource_list(config, signer, compartment.id)
        for resource in resources:
            go = 0
            if (resource.lifecycle_state == 'AVAILABLE'):
                if ('control' in resource.defined_tags) and ('nightly_stop' in resource.defined_tags['control']): 
                    if (resource.defined_tags['control']['nightly_stop'].upper() != 'FALSE'):
                        go = 1
                else:
                    go = 1

            if (go == 1):
                print("    * {} ({}) in {}".format(resource.display_name, resource.lifecycle_state, compartment.name))
                target_resources.append(resource)
            else:
                print("      {} ({}) in {}".format(resource.display_name, resource.lifecycle_state, compartment.name))

    print('\nStopping * marked {}...'.format(resource_name))
    for resource in target_resources:
        try:
            response = _resource_action(config, signer, resource.id)
        except oci.exceptions.ServiceError as e:
            print("---------> error. status: {}".format(e))
            pass
        else:
            if response.lifecycle_state == 'STOPPING':
                print("    stop requested: {} ({})".format(response.display_name, response.lifecycle_state))
            else:
                print("---------> error stopping {} ({})".format(response.display_name, response.lifecycle_state))

    print("\nAll {} stopped!".format(resource_name))

def change_analytics_license(config, signer, compartments):
    target_resources = []

    print("Listing all {}... (* is marked for change)".format(resource_name))

    for compartment in compartments:
        # print("  compartment: {}".format(compartment.name))
        resources = _get_resource_list(config, signer, compartment.id)
        for resource in resources:
            if (resource.license_model == 'LICENSE_INCLUDED'):
                print("    * {} ({}) in {}".format(resource.display_name, resource.license_model, compartment.name))
                target_resources.append(resource)
            else:
                print("      {} ({}) in {}".format(resource.display_name, resource.license_model, compartment.name))

    print("\nChanging * marked {}'s lisence model...".format(resource_name))
    for resource in target_resources:
        try:
            response = _change_license_model(config, signer, resource.id, 'BRING_YOUR_OWN_LICENSE')
        except oci.exceptions.ServiceError as e:
            print("---------> error. status: {}".format(e))
            pass
        else:
            if response.lifecycle_state == 'UPDATING':
                print("    change requested: {} ({})".format(response.display_name, response.lifecycle_state))
            else:
                print("---------> error changing {} ({})".format(response.display_name, response.lifecycle_state))

    print("\nAll {} changed!".format(resource_name))

def _get_resource_list(config, signer, compartment_id):
    object = oci.analytics.AnalyticsClient(config=config, signer=signer)
    resources = oci.pagination.list_call_get_all_results(
        object.list_analytics_instances,
        compartment_id=compartment_id
    )
    return resources.data

def _change_license_model(config, signer, resource_id, license_model):
    object = oci.analytics.AnalyticsClient(config=config, signer=signer)
    details = oci.analytics.models.UpdateAnalyticsInstanceDetails(license_model = license_model)
    response = object.update_analytics_instance(
        resource_id,
        details
    )
    return response.data

def _resource_action(config, signer, resource_id):
    object = oci.analytics.AnalyticsClient(config=config, signer=signer)
    response = object.stop_analytics_instance(
        resource_id
    )
    return response.data
