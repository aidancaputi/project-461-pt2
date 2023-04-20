import os
from database import upload
import json

import flask

app = flask.Flask(__name__)

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

# /packages
@app.route('/packages', methods = ['POST'])
def list_packages():
    all_package_names = queryAllPackages()
    str_resp = str(format(all_package_names))
    response = flask.jsonify({'pkg':str_resp})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

# /package
@app.route('/package', methods = ['POST'])
def add_package():
    # add package to database here -------------------------------------------------
    return "Package added!"

# GET /package/{id}/rate
@app.route("/package/<package_id>/rate")
def get_metrics(package_name):

    #get URL using package ID

    #use the URL to make request to pt1 server

    #format that response as the required json then return it

    return

# /reset
@app.route("/reset", methods = ['DELETE'])
def reset(): 
    #delete all stuff in database here --------------------------------------------------------
    upload.reset_database()
    return

# PUT /package/{id}
@app.route("/package/<id>", methods = ['PUT'])
def put_by_id(id):

    #get the request content json
    """ content = flask.request.get_json()

    #extract all the info from the request json
    put_id = content.get('ID')
    put_name = content.get('Name')
    put_Version = content.get('Version')
    put_content = content.get('Content')
    put_name = content.get('Name')
    put_URL = content.get('URL')
    put_JSProgram = content.get('JSProgram') """
    
    #use request info above to update database now
    
    return


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))