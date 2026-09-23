def clean_checkpoint(res):

    try:
        channel_version_keys = [k for k in res['channel_values'].keys()]

        for k in channel_version_keys:
            if k == "messages" or k == "collection_name":
                pass
            else:
                
                del res['channel_values'][k]


        channel_version_keys = [k for k in res['channel_versions'].keys()]

        for k in channel_version_keys:
            if k in ["__start__", "messages", "collection_name", "branch:to:call_model"]:
                pass
            else:
                del res['channel_versions'][k]

        versions_seen_keys = [k for k in res["versions_seen"].keys()]

        for k in versions_seen_keys:
            if k in ["__input__", "__start__", "call_model"]:
                pass
            else:
                del res['versions_seen'][k]
        
        del res['updated_channels']
    except:
        print("already deleted")
