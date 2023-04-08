# -*- coding: utf-8 -*-

def executePluginRequest(cls, requestObject):
    pluginArgs = requestObject["pluginArgs"]
    pluginName = str(requestObject["pluginName"]).upper()

    if pluginName in cls.plugin.keys():
        try:
            if len(pluginArgs) > 0:
                for commandResult in cls.plugin[pluginName]["cmdEntry"](pluginArgs):
                    yield commandResult
            else:
                for commandResult in cls.plugin[pluginName]["cmdEntry"]():
                    yield commandResult
        except Exception as ex:
            yield {
                "type": "error",
                "message": "Plugin command failed. " + repr(ex),
            }
    else:
        yield {
            "type": "error",
            "message": "Unrecognized plugin command [" + pluginName + "].",
        }
