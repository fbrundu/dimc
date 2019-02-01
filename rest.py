import cherrypy
from cherrypy import log
from lib import get_parameters, handle_error
import json
# import os
import requests
import ssl
# import subprocess as sp
import urllib
from xml.etree import ElementTree

# load configuration into global dictionary
with open("conf/conf.json", "r") as cfile:
    pbc = json.load(cfile)

# FIXME TEMPORARY
districts_map = {
                "TU": ["ITC11-" + str(i).zfill(2) for i in range(1, 8)],
                 "MA": ["UKD33-" + str(i).zfill(2) for i in range(1, 27)]
                }
storeymap = {}
# storeymap[]
###

bimprovider_url = pbc["bimpurl"]


# Ping microservice
class Ping(object):
    exposed = True

    def GET(self, **params):

        if validate(cherrypy.request.headers):
            try:
                return handle_error(200, "Pong")
            except:
                return handle_error(500, "Internal Server Error")
        else:
            return handle_error(401, "Unauthorized")


# PingThru microservice
class PingThru(object):
    exposed = True

    def GET(self, **params):

        if validate(cherrypy.request.headers):
            try:
                # basic ping response through the infrastructure
                r = requests.get(urllib.parse.urljoin(bimprovider_url, "ping"))

                # return response
                return handle_error(200, r.json()["message"] + "thru")
            except:
                return handle_error(500, "Internal Server Error")
        else:
            return handle_error(401, "Unauthorized")


# GetJSON microservice
class GetJSON(object):
    exposed = True

    def GET(self, *paths, **params):

        if validate(cherrypy.request.headers):
            try:
                # get buildings as JSON array
                url = urllib.parse.urljoin(bimprovider_url, "getjson")
                response = query(url, params)

                ctype = "application/json;charset=utf-8"
                cherrypy.response.headers["Content-Type"] = ctype

                # return response
                return response
            except:
                return handle_error(500, "Internal Server Error")
        else:
            return handle_error(401, "Unauthorized")


# GetIFC microservice
class GetIFC(object):
    exposed = True

    def GET(self, *paths, **params):

        if validate(cherrypy.request.headers):
            try:
                # get zip of ifcs
                url = urllib.parse.urljoin(bimprovider_url, "getifc")
                response = get_resources(url, params)

                # set response header for zip
                cherrypy.response.headers["Content-Type"] = "application/zip"
                cdisp = 'attachment; filename="resp.zip"'
                cherrypy.response.headers["Content-Disposition"] = cdisp

                return response
            except:
                return handle_error(500, "Internal Server Error")
        else:
            return handle_error(401, "Unauthorized")


# GetGBXML microservice
class GetGBXML(object):
    exposed = True

    def GET(self, *paths, **params):

        if validate(cherrypy.request.headers):
            try:
                # get zip of gbxmls
                url = urllib.parse.urljoin(bimprovider_url, "getgbxml")
                response = get_resources(url, params)

                # set response header for zip
                cherrypy.response.headers["Content-Type"] = "application/zip"
                cdisp = 'attachment; filename="resp.zip"'
                cherrypy.response.headers["Content-Disposition"] = cdisp

                return response
            except:
                return handle_error(500, "Internal Server Error")
        else:
            return handle_error(401, "Unauthorized")


# GetRVT microservice
class GetRVT(object):
    exposed = True

    def GET(self, *paths, **params):

        if validate(cherrypy.request.headers):
            try:
                # get zip of rvts
                url = urllib.parse.urljoin(bimprovider_url, "getrvt")
                response = get_resources(url, params)

                # set response header for zip
                cherrypy.response.headers["Content-Type"] = "application/zip"
                cdisp = 'attachment; filename="resp.zip"'
                cherrypy.response.headers["Content-Disposition"] = cdisp

                return response
            except:
                return handle_error(500, "Internal Server Error")
        else:
            return handle_error(401, "Unauthorized")


# Query microservice
class Query(object):
    exposed = True

    def GET(self, *paths, **params):

        if validate(cherrypy.request.headers):
            try:
                # query
                url = urllib.parse.urljoin(bimprovider_url, "query")
                response = query(url, params)
                ctype = "application/json;charset=utf-8"
                cherrypy.response.headers["Content-Type"] = ctype

                # return response
                return response
            except:
                return handle_error(500, "Internal Server Error")
        else:
            return handle_error(401, "Unauthorized")


# to start the Web Service
def start():

    # start the service registrator utility (deprecated, now we use sreg)
    # p = sp.Popen([
    #     os.path.join(pbc["binpath"], "service-registrator"),
    #     "-conf", pbc["confpath"],
    #     "-endpoint", pbc["scatalog"],
    #     "-authProvider", pbc["aprovider"],
    #     "-authProviderURL", pbc["aurl"],
    #     "-authUser", pbc["auser"],
    #     "-authPass", pbc["apass"],
    #     "-serviceID", pbc["aserviceID"]])

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ctx.options |= ssl.OP_NO_SSLv2
    ctx.options |= ssl.OP_NO_SSLv3

# ciphers = {
#     'DHE-RSA-AE256-SHA',
#     ...
#     'RC4-SHA'
# }

# ctx.set_cipher_list(':'.join(ciphers))

    # start Web Service with some configuration
    if pbc["stage"] == "production":
        global_conf = {
               "global":    {
                              "server.environment": "production",
                              "engine.autoreload.on": True,
                              "engine.autoreload.frequency": 5,
                              "server.socket_host": "0.0.0.0",
                              "server.socket_port": 443,
                              # "server.socket_port": 8082,
                              "server.ssl_module": "builtin",
                              "server.ssl_certificate": pbc["cert"],
                              "server.ssl_private_key": pbc["priv"],
                              "server.ssl_certificate_chain": pbc["chain"],
                              "server.ssl_context": ctx,
                              "log.screen": False,
                              "log.access_file": "dimc.log",
                              "log.error_file": "dimc.log"
                            }
        }
        cherrypy.config.update(global_conf)
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.encode.debug": True,
            "request.show_tracebacks": False
        }
        # "/dimc/getjson": {
        #     # "tools.encode.on": True,
        # }
    }

    cherrypy.tree.mount(Ping(), '/dimc/ping', conf)
    cherrypy.tree.mount(PingThru(), '/dimc/pingthru', conf)
    cherrypy.tree.mount(GetJSON(), '/dimc/getjson', conf)
    cherrypy.tree.mount(GetIFC(), '/dimc/getifc', conf)
    cherrypy.tree.mount(GetGBXML(), '/dimc/getgbxml', conf)
    cherrypy.tree.mount(GetRVT(), '/dimc/getrvt', conf)
    cherrypy.tree.mount(Query(), '/dimc/query', conf)

    # activate signal handler
    if hasattr(cherrypy.engine, "signal_handler"):
        cherrypy.engine.signal_handler.subscribe()

    # subscribe to the stop signal
    # cherrypy.engine.subscribe("stop", p.terminate)

    # start serving pages
    cherrypy.engine.start()
    cherrypy.engine.block()


def validate(headers):

    validated = False

    try:
        token = headers["X-Auth-Token"]
        url = (pbc["aurl"] + "/p3/serviceValidate?" +
               "service=bimServiceProvider&ticket=" +
               token)
        r = requests.get(url, verify=pbc["acert"])
        root = list(ElementTree.fromstring(r.content))
        validated = root[0].tag.endswith("authenticationSuccess")
    except Exception:
        log.error(msg="Validation Error", context="HTTP", traceback=True)
        validated = False

    return validated


def query(bimprovider_url, params):

    url = ask_bimprovider(bimprovider_url, params)

    r = requests.get(url)

    if r.status_code != 200:
        raise cherrypy.HTTPError(str(r.status_code), "")

    return r.content


def ask_bimprovider(bimprovider_url, params):

    try:
        districts = get_parameters(params, "district")
        buildings = []
    except:
        # FIXME temp fallback
        districts = []
        buildings = get_parameters(params, "building")

    try:
        typologies = get_parameters(params, "typology")
    except:
        typologies = None

    try:
        heatings = get_parameters(params, "heating")
    except:
        heatings = None

    unchanged = {key: value
                 for (key, value) in params.items()
                 if key not in ("building", "district", "typology", "heating")}

    unchanged = urllib.parse.urlencode(unchanged, doseq=True)

    url = bimprovider_url + "?" + unchanged

    if len(unchanged) > 0:
        url += "&"

    url += get_buildings_url(get_buildings(bimprovider_url, districts,
                                           buildings, typologies, heatings))

    return url


def get_resources(bimprovider_url, params):

    url = ask_bimprovider(bimprovider_url, params)

    r = requests.get(url)

    if r.status_code != 200:
        raise cherrypy.HTTPError(str(r.status_code), "")

    return r.content


def get_buildings_url(buildings):

    buildings = ["building=" + b for b in buildings]
    url = "&".join(buildings)

    return url


def get_buildings(bimp_url, districts, buildings, typologies=None,
                  heatings=None):

    if "*" in districts:
        districts = districts_map.keys()
    if len(districts) > 0:
        buildings += districts_to_buildings(districts)

    if typologies is not None or heatings is not None:
        buildings = filter_buildings(bimp_url, buildings, typologies, heatings)

    return set(buildings)


def districts_to_buildings(districts):

    buildings = []

    for c in districts:
        buildings += districts_map[c]

    return buildings


def filter_buildings(bimp_url, buildings, typologies=None, heatings=None):

    url = urllib.parse.urljoin(bimp_url, "query")

    parameters = [("gettypology", typologies),
                  ("getheatingsupply", heatings)]

    for qname, filters in parameters:
        if filters is not None:
            lurl = url + "?qname=" + qname
            lurl += "".join(["&building=" + b for b in buildings])
            r = requests.get(lurl)

            if r.status_code != 200:
                raise cherrypy.HTTPError(str(r.status_code), "")

            result = r.json()
            result = result["q_res"]
            buildings = [b["b_id"] for b in result if b["b_res"][0] in filters]

    return buildings
