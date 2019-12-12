import urllib.request, urllib.error, urllib.parse, json
import webapp2, os, urllib
import jinja2

import logging
### No API key is needed for this project

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info("In MainHandler")
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class ResponseHandler(webapp2.RequestHandler):
    def get(self):
        vals = {}
        vals['page_title'] = "Visualization Response"
        countrycode = self.request.get('countrycode')
        startyr = self.request.get('date')
        go = self.request.get('submit')
        logging.info(countrycode)
        logging.info(startyr)
        logging.info(go)
        # no need to worry about whether the inputs are filled in or not, because a drop down menu and radio
        # buttons always have an option filled in
        vals['precip'] = getPrecipiation(countrycode, startyr)
        vals['temp'] = getTemp(countrycode, startyr)
        template = JINJA_ENVIRONMENT.get_template('response.html')
        self.response.write(template.render(vals))

# pick handlers based on URL
application = webapp2.WSGIApplication([ \
    ('/.*', MainHandler),
    ('/response', ResponseHandler)
],
    debug=True)

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeGet(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None

#format for rest call
#/v1/country/type[/GCM][/SRES]/var/start/end/ISO3
def climateREST(country,
    var,
    baseurl = 'http://climatedataapi.worldbank.org/climateweb/rest/',
    type = 'mavg',
    scenario = "a2",
    GCM = "csiro_mk3_5",
    start = "2020",
    printurl=False,
    ):
    if start == "2020":
        end = "2039"
    elif start == "2040":
        end = "2059"
    elif start == "2060":
        end = '2079'
    else:
        end = "2099"
    url = baseurl + "v1/country/" + type + "/" + GCM + "/" + scenario + "/" + var + "/" + start + "/" + end + "/" + country;
    if printurl:
        print(url)
    return safeGet(url)

def getPrecipiation(countrycode, startyr=2020):
    precip = json.load(climateREST(countrycode, "pr", start = startyr))
    return precip[0]["monthVals"] #returns 12 element array with average precipitation for each month


def getTemp(countrycode, startyr=2020):
    temp = json.load(climateREST(countrycode, "pr", start = startyr))
    return temp[0]["monthVals"] #returns 12 element array with average temperature for each month