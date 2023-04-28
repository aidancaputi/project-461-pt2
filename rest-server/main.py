import os
from database import databaseFunctions
import base64
import flask
from git import Repo
import pathlib
import zipfile
import shutil
import os
import json
from os import path
import stat
import requests

app = flask.Flask(__name__)

@app.route('/', methods = ['GET'])
def plain():
    return 'Project homepage'

# /packages
@app.route('/packages', methods = ['POST'])
def search_packages():

    return_list = []
    
    #request has name and version
    request_content = flask.request.get_json()
    #print(request_content)
    name = request_content['Name']
    version = request_content['Version']

    #get the exact version number
    versions = version.split('\n')
    exact_version = versions[0].split('(')[1]
    exact_version = exact_version.split(')')[0]

    #get json of all packages in database
    packages_json = json.loads(databaseFunctions.get_all_packages())
    #print(packages_json)

    #go through the packages and return a match if there is one
    for package in packages_json:

        if((package['Version'] == exact_version) and (package['Name'] == name)):
            
            #format and return 
            return_list.append(package)

    #turn the list of packages into json and return it
    return_json = json.dumps(return_list)

    print("packges found that match query: "+ str(return_list))

    return return_json

#takes a path to a folder and zips it, then encodes the zip into a base64 string
def encode_repo(repo_path):

    print("enter encoding function")
    
    #zip the folder
    shutil.make_archive("repo_zip", 'zip', repo_path)

    #encode the zip
    with open("repo_zip.zip", "rb") as zipfile:
        encoded = base64.b64encode(zipfile.read())

    #return the encoded zip file
    print("package encoded successfully")

    # make sure the encoding is a string
    return str(encoded)

#takes a base 64 encoding then decodes and unzips it
def convert_base64_and_unzip(encoded):

    print("decoding base64")

    #open a zip and write the decoded file to it
    with open('output_file.zip', 'wb') as result:
        result.write(base64.b64decode(encoded))

    #extract that file into folder with the name "cloned_repo"
    zip_ref = zipfile.ZipFile("output_file.zip", 'r')
    zip_ref.extractall("cloned_repo") 
    zip_ref.close()

    print("base64 decoded into directory")

#finds the package.json file in a folder and returns the path
def find_package_json(path):
    print("finding package.json in local clone")
    filename = "package.json"
    for root, dirs, files in os.walk(path):
        if filename in files:
            print("found package.json")
            return os.path.join(root, filename)
    print("didnt find package.json")
    return "fail to find package.json"

#gets the metadata for the cloned repo
def parse_for_info(need_url):
    
    print("enter parse for info")

    #find package.json in the cloned repo
    filepath = find_package_json("cloned_repo")

    #open the json file
    package_json_file = open(filepath)

    #get the json data
    package_data = json.load(package_json_file)

    #get name and version
    name = package_data['name']
    version = package_data['version']

    #if we needed to get the url from the package json
    if(need_url == True):
        try: 
            url = package_data['repository']['url']
        except:
            url = None
        print("returning name, version, and url from parse for info")
        return name, version, url
    
    print("returning name and version from parse for info")
    #if we didnt need the url, just return the name and version
    return name, version

#delete the given directory
def clean_up(cloned_dir, was_encoding):

    print("enter clean up")

    #delete the cloned repo
    for root, dirs, files in os.walk("./cloned_repo"):  
        for dir in dirs:
            os.chmod(path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(path.join(root, file), stat.S_IRWXU)
    shutil.rmtree('./cloned_repo')

    if(was_encoding == True):
        os.remove("repo_zip.zip")

# /package
@app.route('/package', methods = ['POST'])
def add_package():
    # add package to database here -------------------------------------------------
    
    print("enter post /package")
    request_content = flask.request.get_json()
    content = 0
    url = 0

    try:
        clean_up("cloned_repo", True)
    except:
        pass

    #got content and not url
    if ('Content' in request_content) and ('URL' not in request_content):

        print("got content but not url")

        content = request_content['Content']

        #if encoded was set, decode it and unzip
        convert_base64_and_unzip(content)

        #parse the unzipped repo for the name, version, and url
        package_name, package_version, package_url = parse_for_info(need_url=True)

        #if it didnt find one of the infos, return 400
        package_info_list = [package_name, package_version, package_url]
        for x in package_info_list:
            if x == None:
                clean_up("cloned_repo", False)
                print("didnt find a necessary info on the repo, returning 400")
                return '{}', 400

        #upload to database
        print("calling upload_package")
        database_confirmation = databaseFunctions.upload_package(package_name, package_version, content, package_url, request_content['JSProgram'])

        #if it alreayd existed in database, clean and exit
        if(database_confirmation == 409):
            clean_up("cloned_repo", False)
            print("package already existed, returning 409")
            return "Package already exists", 409
        
        #print(package_name, package_version, package_url, request_content['JSProgram'])

        clean_up("cloned_repo", False)

    #got url and not content
    elif ('URL' in request_content) and ('Content' not in request_content):
        
        print("got url but not content")
        url = request_content['URL']
        
        #clone the url
        Repo.clone_from(url, "cloned_repo")
        print("repo cloned")

        #parse the local repo for the name and version
        package_name, package_version = parse_for_info(need_url=False)

        #if it didnt find one of the infos, return 400
        package_info_list = [package_name, package_version, url]
        for x in package_info_list:
            if x == None:
                clean_up("cloned_repo", True)
                print("didnt find a necessary info on the repo, returning 400")
                return '{}', 400

        #encode the cloned repo
        encoding = encode_repo("cloned_repo")

        #upload to database
        print("calling upload package with content: " + encoding[:50])
        database_confirmation = databaseFunctions.upload_package(package_name, package_version, encoding, url, request_content['JSProgram'])

        #if it already existed, clean and exit
        if(database_confirmation == 409):
            clean_up("cloned_repo", True)
            print("package already existed, returning 409")
            return "Package already exists", 409
        
        #print(package_name, package_version, package_url, request_content['JSProgram'])

        clean_up("cloned_repo", True)

    else: 

        print("both or neither content/url were set, bad requst 400")
        #this would be if both or neither field were set
        return "Bad request", 400

    return_json = json.dumps(database_confirmation)    

    print("post /package success")

    return return_json

# GET /package/{id}/rate
@app.route("/package/<package_id>/rate", methods = ["GET"])
def get_metrics(package_id):

    print("enter get /rate for id: "+ str(package_id))

    #get package info from database
    print("getting info on id from database")
    db_resp = databaseFunctions.get_package(package_id)
    print("got info on id from database")

    #get url from content
    url = db_resp['data']['URL']
    print("found url in the database response")

    #use the URL to make request to pt1 server
    print("making request to pt1 server")
    response = requests.get('https://pt1-server-h5si5ezrea-uc.a.run.app' + '/' + url)
    print("got response from pt1 server: "+ str(response.content))

    return response.content

# /reset
@app.route("/reset", methods = ['DELETE'])
def reset(): 
    print("delete /reset enter")
    databaseFunctions.reset_database()
    print("database reset success")
    response = flask.jsonify(success=True)
    print("responding 200 ok about delete reset")
    return response

# PUT /package/{id}
@app.route("/package/<id>", methods = ['PUT','GET','DELETE'])
def put_by_id(id):

    print("enter /package/id with method: " + str(flask.request.method))

    if flask.request.method == 'PUT':

        print("it was put, getting request content")
        #get the request content json
        request_content = flask.request.get_json()

        print("request content got succesfuly from request")

        #extract all the info from the request json
        put_id = request_content['metadata']['ID']
        put_name = request_content['metadata']['Name']
        put_Version = request_content['metadata']['Version']
        put_content = request_content['data']['Content']
        put_URL = request_content['data']['URL']
        put_JSProgram = request_content['data']['JSProgram']

        print("got all fields from request successfully")

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
    print("authenticate called, returning 501")
    return "Not Implemented",501

@app.route("/package/byName/<name>", methods = ['GET','DELETE'])
def pkgbyName(name):
    print("package byName entered with method: " + str(flask.request.method))
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