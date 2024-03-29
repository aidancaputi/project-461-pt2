import os
from database import databaseFunctions
import base64
import flask
from git import Repo
import zipfile
import shutil
import os
import json
from os import path
import stat
import requests
import re

app = flask.Flask(__name__)

@app.route('/', methods = ['GET'])
def plain():
    return 'Welcome to Aidan, Zane, and Josh\'s 461 Project Backend'

def look_for_package(name, version, type):
    
    counter = 0
    return_list = []
    packages_json = json.loads(databaseFunctions.get_all_packages())

    if type == 'exact':
        print('type was exact')
        #go through all the packages returned from database
        for package in packages_json:
            
            #if the package matches the query
            if((package['Version'] == version) and (package['Name'] == name)):
                
                #format and return 
                return_list.append(package)

                counter += 1

                #if there were more than 1000 packages that match, return 413
                if(counter > 1000):
                    return "Too many packages matched that query (> 1000)", 413
                
    if type == 'range':
        print('type was range')
        lower = version[0].replace('.', ', ')
        upper = version[1].replace('.', ', ')
        lower_tup = tuple(map(int, lower.split(', ')))
        upper_tup = tuple(map(int, upper.split(', ')))
       

        #go through all the packages returned from database
        for package in packages_json:
            package_tup = tuple(map(int, package['Version'].split('.')))

            #if the package matches the query
            if((package_tup >= lower_tup) and (package_tup <= upper_tup) and (package['Name'] == name)):
                
                #format and return 
                return_list.append(package)

                counter += 1

                #if there were more than 1000 packages that match, return 413
                if(counter > 1000):
                    return "Too many packages matched that query (> 1000)", 413
                
    if type == 'carrot':
        print('type was carrot')
        lower = version.replace('.', ', ')
        lower_tup = tuple(map(int, lower.split(', ')))

        #go through all the packages returned from database
        for package in packages_json:

            package_tup = tuple(map(int, package['Version'].split('.')))
            
            #if the package matches the query
            if((package_tup >= lower_tup) and (package['Name'] == name)):
                
                #format and return 
                return_list.append(package)

                counter += 1

                #if there were more than 1000 packages that match, return 413
                if(counter > 1000):
                    return "Too many packages matched that query (> 1000)", 413
                
    if type == 'tilde':

        upper = version.replace('.', ', ')
        upper_tup = list(map(int, upper.split(', ')))

        orig_tup = tuple(map(int, upper.split(', ')))

        upper_tup[1] = upper_tup[1] + 1
        upper_tup[2] = 0
        upper_tup = tuple(upper_tup)
        
        print('type was tilde')

        #go through all the packages returned from database
        for package in packages_json:

            package_tup = tuple(map(int, package['Version'].split('.')))

            #if the package matches the query
            if((package_tup >= orig_tup) and (package_tup <= upper_tup) and (package['Name'] == name)):
                
                #format and return 
                return_list.append(package)

                counter += 1

                #if there were more than 1000 packages that match, return 413
                if(counter > 1000):
                    return "Too many packages matched that query (> 1000)", 413
    
    return return_list

# POST /packages
@app.route('/packages', methods = ['POST'])
def search_packages():

    #request has name and version
    request_content = flask.request.get_json()
    print(request_content)
    return_list = []


    for item in request_content:

        name = item['Name']
        version = item['Version']

        #if there was a dash, its a range
        if '-' in version:
            
            #range
            both_versions = version.split('-')
           
            resp = look_for_package(name,both_versions, 'range')
            
            if len(resp) == 2:
                if resp[1] == 413:
                    return "Too many packages matched that query (> 1000)", 413
            return_list += resp
            
        elif '^' in version:
            #carrot
            lower_version = version.replace('^', '')
            resp = look_for_package(name, lower_version, 'carrot')
            if len(resp) == 2:
                if resp[1] == 413:
                    return "Too many packages matched that query (> 1000)", 413
                
            return_list += resp
        
        elif '~' in version:
            #tilde
            approx_version = version.replace('~', '')
            resp = look_for_package(name, approx_version, 'tilde')
            if len(resp) == 2:
                if resp[1] == 413:
                    return "Too many packages matched that query (> 1000)", 413
            return_list += resp
        
        else:
            #exact
            exact_version = version
            resp = look_for_package(name, exact_version, 'exact')
            if len(resp) == 2:
                if resp[1] == 413:
                    return "Too many packages matched that query (> 1000)", 413
            return_list += resp
    
    final_list = []

    for item in return_list:
        if item not in final_list:
            final_list.append(item)

    #turn the list of packages into json and return it
    return_json = json.dumps(final_list)
    
    print("packages found that match query: "+ str(final_list))

    return return_json, 200

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
    return encoded

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
def clean_up():

    print("enter clean up")

    try:
        #delete the cloned repo
        for root, dirs, files in os.walk("./cloned_repo"):  
            for dir in dirs:
                os.chmod(path.join(root, dir), stat.S_IRWXU)
            for file in files:
                os.chmod(path.join(root, file), stat.S_IRWXU)
        shutil.rmtree('./cloned_repo')

        os.remove("repo_zip.zip")
        
        print("clean up success")

    except:
        print("there was nothing to clean up")
        pass

# /package
@app.route('/package', methods = ['POST'])
def add_package():
    # add package to database here -------------------------------------------------
    
    print("enter post /package")
    request_content = flask.request.get_json()
    content = 0
    url = 0
    print(request_content)

    clean_up()

    #got content and not url
    if (request_content['URL'] == None) and (request_content['Content'] != None):

        print("got content but not url")

        content = request_content['Content']

        #if encoded was set, decode it and unzip
        convert_base64_and_unzip(content)

        #parse the unzipped repo for the name, version, and url
        package_name, package_version, package_url = parse_for_info(need_url=True)

        if(package_url == None):
            return "There is missing field(s) in the PackageData/AuthenticationToken or it is formed improperly (e.g. Content and URL are both set), or the AuthenticationToken is invalid.", 400

        #if it didnt find one of the infos, return 400
        if(package_name == None) or (package_version == None):
            clean_up()
            print("didnt find a necessary info on the repo, returning 400")
            return 'There is missing field(s) in the PackageData/AuthenticationToken or it is formed improperly (e.g. Content and URL are both set), or the AuthenticationToken is invalid.', 400
                
        #upload to database
        database_confirmation = databaseFunctions.upload_package(package_name, package_version, content, package_url, request_content['JSProgram'])

        #if it alreayd existed in database, clean and exit
        if(database_confirmation == 409):
            clean_up()
            print("package already existed, returning 409")
            return "Package exists already.", 409

        clean_up()

    #got url and not content
    elif (request_content['URL'] != None) and (request_content['Content'] == None):
        
        print("got url but not content")
        url = request_content['URL']
        
        #clone the url
        Repo.clone_from(url, "cloned_repo")

        #parse the local repo for the name and version
        package_name, package_version = parse_for_info(need_url=False)

        #if it didnt find one of the infos, return 400
        if(package_name == None) or (package_version == None):
            clean_up()
            print("didnt find a necessary info on the repo, returning 400")
            return 'There is missing field(s) in the PackageData/AuthenticationToken or it is formed improperly (e.g. Content and URL are both set), or the AuthenticationToken is invalid.', 400

        #encode the cloned repo
        encoding = encode_repo("cloned_repo")

        #upload to database
        database_confirmation = databaseFunctions.upload_package(package_name, package_version, encoding, url, request_content['JSProgram'])

        #if it already existed, clean and exit
        if(database_confirmation == 409):
            clean_up()
            print("package already existed, returning 409")
            return "Package exists already.", 409
        
        #print(package_name, package_version, package_url, request_content['JSProgram'])

        clean_up()

    else: 

        print("both or neither content/url were set, bad request 400")
        #this would be if both or neither field were set
        return "There is missing field(s) in the PackageData/AuthenticationToken or it is formed improperly (e.g. Content and URL are both set), or the AuthenticationToken is invalid.", 400

    return_json = database_confirmation

    print("post /package success")

    return return_json,201

# GET /package/{id}/rate
@app.route("/package/<package_id>/rate", methods = ["GET"])
def get_metrics(package_id):

    print("enter get /rate for id: "+ str(package_id))

    #get package info from database
    db_resp = databaseFunctions.get_package(package_id)

    if db_resp == 404:
        return 'Package does not exist.',404
    else:
        #get url from content
        url = db_resp['data']['URL']

        #use the URL to make request to pt1 server
        print("making request to pt1 server")
        response = requests.get('https://pt1-server-h5si5ezrea-uc.a.run.app' + '/' + url)
        print("got response from pt1 server: "+ str(response.content),type(response.content))
        
        resp_real = json.loads(response.content)
        print('resp_real',resp_real,type(resp_real))
        resp_curr = resp_real[0]
        print('resp_curr',resp_curr,type(resp_curr))

        return resp_curr,200


# /reset
@app.route("/reset", methods = ['DELETE'])
def reset(): 
    print("delete /reset enter")
    databaseFunctions.reset_database()
    print("database reset success")
    return 'Registry is reset.', 200

# PUT /package/{id}
@app.route("/package/<id>", methods = ['PUT','GET','DELETE'])
def put_by_id(id):

    print("enter /package/id with method: " + str(flask.request.method))

    if flask.request.method == 'PUT':

        print("it was put, getting request content")
        #get the request content json
        request_content = flask.request.get_json()
        print(request_content)

        #extract all the info from the request json and return 400 if missing something
        try:
            put_id = request_content['metadata']['ID']
            put_name = request_content['metadata']['Name']
            put_Version = request_content['metadata']['Version']
            put_content = request_content['data']['Content']
            put_URL = request_content['data']['URL']
            put_JSProgram = request_content['data']['JSProgram']
        except:
            print("error reading fields from request")
            return 'There is missing field(s) in the PackageID/AuthenticationToken or it is formed improperly, or the AuthenticationToken is invalid.', 400

        # if no URL, find it from content
        if put_URL == None:
            content = request_content['data']['Content']

            #if encoded was set, decode it and unzip
            convert_base64_and_unzip(content)

            #parse the unzipped repo for the name, version, and url
            package_url = parse_for_info(need_url=True)[2]

            put_URL = package_url

        #use request info above to update database now
        db_resp = databaseFunctions.update_package(put_name, put_Version, put_id, put_content, put_URL, put_JSProgram)

        print("update_package returned")

        if(db_resp == 200):
            return 'Version is updated.', 200

        return 'Package does not exist.', 404
    
    elif flask.request.method == 'GET':
        # send query to get <id> in variable id
        db_resp = databaseFunctions.get_package(id)

        #if the package wasnt in the database, return 404
        if(db_resp == 404):
            return "Package does not exist.", 404
        
        return_json = db_resp

        return return_json
    
    elif flask.request.method == 'DELETE':
        # send query to delete <id> in variable id

        db_resp = databaseFunctions.delete_package(id)

        if(db_resp == 404):
            return "Package does not exist.", 404
        
        return "Package is deleted.", 200

@app.route("/authenticate", methods = ['PUT'])

def authenticate():
    # authenticate not implemented
    print("authenticate called, returning 501")
    return "This system does not support authentication.",501

@app.route("/package/byName/<name>", methods = ['GET','DELETE'])
def pkgbyName(name):
    print("package byName entered with method: " + str(flask.request.method))
    if flask.request.method == 'GET':
        
        resp = databaseFunctions.get_package_history(name)

        if resp == 404:
            return 'Package does not exist.',404
        
        return resp
        
    # query database using name variable
    elif flask.request.method == 'DELETE':
        # delete name from database

        resp = databaseFunctions.delete_history(name)

        if resp == 404:
            return 'Package does not exist.',404
        
        return 'Package is deleted.'

@app.route("/package/byRegEx", methods = ['POST'])
def byRegEx():
    match_pkgs = []

    request_content = flask.request.get_json()

    try:
        reg = request_content['RegEx']
        print(reg)
    except:
        return 'There is missing field(s) in the PackageRegEx/AuthenticationToken or it is formed improperly, or the AuthenticationToken is invalid.',400
    
    all_pkgs = json.loads(databaseFunctions.get_all_packages())
    
    for p in all_pkgs:
        print(p)
        currName = p['Name']
        if re.match(reg,currName) is not None:
            p.pop('ID')
            temp = p
            match_pkgs.append(temp)
    
    print('matched packages',match_pkgs)

    if len(match_pkgs) == 0:
        return 'No package found under this regex.',404

    return_json = flask.jsonify(match_pkgs)
    print(return_json,type(return_json))

    return return_json


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))