import os
from database import databaseFunctions
import base64
import flask
import base64
from git import Repo
import pathlib
import zipfile
import shutil
import os
import json
from os import path
import stat

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

def convert(encoded):

    #open a zip and write the decoded file to it
    with open('output_file.zip', 'wb') as result:
        result.write(base64.b64decode(encoded))

    #extract that file into folder with the name "cloned_repo"
    zip_ref = zipfile.ZipFile("output_file.zip", 'r')
    zip_ref.extractall("cloned_repo") 
    zip_ref.close()

def find_package_json(path):
    filename = "package.json"
    for root, dirs, files in os.walk(path):
        if filename in files:
            return os.path.join(root, filename)

#gets name, version, and url from cloned repo
def parse_for_info():

    #find package.json in the cloned repo
    filepath = find_package_json("cloned_repo")

    #print(filepath)

    #open the json file
    package_json_file = open(filepath)

    #get the json data
    package_data = json.load(package_json_file)

    #get name and version
    name = package_data['name']
    version = package_data['version']
    try: 
        url = package_data['repository']['url']
    except:
        url = None

    return name, version, url

#delete the directory
def clean_up(cloned_dir):
    for root, dirs, files in os.walk("./cloned_repo"):  
        for dir in dirs:
            os.chmod(path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(path.join(root, file), stat.S_IRWXU)
    shutil.rmtree('./cloned_repo')

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
        
        #if url was set, clone it to current directory
        Repo.clone_from(url, "cloned_repo")

        #then, call parse function for info we need
        package_name, package_version, package_url = parse_for_info()

        clean_up("cloned_repo")

        databaseFunctions.upload_package(package_name, package_version, None, package_url)
        pass
    else:
        #add content to database

        #if encoded was set, decode it and unzip
        convert(content)

        #then, call parse function for info we need
        name, version, url = parse_for_info()

        clean_up("cloned_repo")

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