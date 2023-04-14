import os
from database import upload

import flask

app = flask.Flask(__name__)

#this is a dummy function to get the metrics that would be returned from part 1 code
#in practice, this would call the part 1 code on the package provided
def getMetrics(package_name):
    test_metrics = {
        package_name : {"URL": package_name, 
                        "NET_SCORE": 1.0, 
                        "RAMP_UP_SCORE": 1.0, 
                        "CORRECTNESS_SCORE": 1.0, 
                        "BUS_FACTOR_SCORE": 1.0, 
                        "RESPONSIVE_MAINTAINER_SCORE": 1.0, 
                        "LICENSE_SCORE": 1.0},
        }
    return test_metrics

#this is a dummy function that would query the database for all the package names we have
#in practice, this will connect to the database and get a list of all package names in the database
def queryAllPackages():
    test_packages = ["lodash", "pytorch", "tensorflow"]
    return test_packages

#this is a dummy function that would get all information about the package from the database and display it
#in practice, this will connect to the database and get all info about a certain package
def getPackageInfo(package_name):
    test_info = {
        package_name : {"name": package_name, 
                        "users": 1000, 
                        "downloads": 69, 
                        "stars": 100, 
                        "description": "This package does x, y, and z for you",
                        },
        }
    return test_info

#this is the home url of the server
@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)

@app.route("/createtable")
def hello_world():
    upload.create_table() 
    return "Created table!"

#this is the packages url, it should list all the packages we have
@app.route('/packages')
def list_packages():
    all_package_names = queryAllPackages()
    str_resp = str(format(all_package_names))
    response = flask.jsonify({'pkg':str_resp})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

#this be the "info page" about a certain package
#it should list the general information about a package
@app.route("/packages/<package_name>")
def package_info(package_name):
    info = getPackageInfo(package_name)
    return "Here is the information we have on the package you wanted:\n {}!".format(info)

#this will be the metrics page for a certain object
#it will run the part 1 code on the package
@app.route("/packages/<package_name>/metrics")
def get_metrics(package_name):
    package_metrics = getMetrics(package_name)
    return "Here are the metrics you asked for:\n {}!".format(package_metrics)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))