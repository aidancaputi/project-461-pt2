import os
from database import databaseFunctions
import base64
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
    request_content = flask.request.get_json()
    content = 0
    url = 0

    try:
        content = request_content['Content']
    except:
        url = request_content['URL']
    
    if content == 0:
        # url

        package_name = 'get_package_name'
        package_version = 'get_package_version'
        package_url = 'get_package_url'
        databaseFunctions.upload_package(package_name, package_version, None, package_url)
        pass
    else:
        #add content to database

        package_name = 'get_package_name'
        package_version = 'get_package_version'
        package_zip = 'get_zip_file'
        databaseFunctions.upload_package(package_name, package_version, package_zip, None)
        pass

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
    databaseFunctions.reset_database()
    return

# PUT /package/{id}

@app.route("/package/<id>", methods = ['PUT','GET','DELETE'])
def put_by_id(id):

    if flask.request.method == 'PUT':
        #get the request content json
        request_content = flask.request.get_json()

        #extract all the info from the request json
        put_id = request_content['metadata']['ID']
        put_name = request_content['metadata']['Name']
        put_Version = request_content['metadata']['Version']
        put_content = request_content['data']['Content']
        put_URL = request_content['data']['URL']
        put_JSProgram = request_content['data']['JSProgram']

        #use request info above to update database now
        
        return str(put_id) + " " + str(id)
    
    elif flask.request.method == 'GET':
        # send query to get <id> in variable id

        return str(id)
    
    elif flask.request.method == 'DELETE':
        # send query to delete <id> in variable id

        return str(id)

@app.route("/authenticate", methods = ['PUT'])

def authenticate():
    # authenticate not implemented

    return "Not Implemented",501

@app.route("/package/byName/<name>", methods = ['GET','DELETE'])

def pkgbyName(name):
    if flask.request.method == 'GET':
        pass
        # query database using name variable
    elif flask.request.method == 'DELETE':
        pass
        # delete name from database
    
    return

# @app.route("/package/byRegEx", methods = ['POST'])
# def byRegEx():





if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))