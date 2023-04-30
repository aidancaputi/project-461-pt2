import re
import json
from database import databaseFunctions

# reg = 'a*'
# result = [['a','b','b'],['c','d','e']]
# all_pkgs = []

# for row in result:
#         package = {
#             'Version': row[0],
#             'Name': row[1],
#             'ID': row[2]
#         }
#         all_pkgs.append(package)

# all_pkgs = json.dumps(all_pkgs)
# all_pkgs = json.loads(all_pkgs)

# match_pkgs = []

# for p in all_pkgs:
#         currID = p['Name']
#         if re.match(reg,currID) is not None:
#             p.pop('ID')
#             temp = p
#             match_pkgs.append(temp)

# print(match_pkgs)


def look_for_package(name, version, type):
    
    counter = 0
    return_list = []
    packages_json = json.loads(databaseFunctions.get_all_packages())
    print('inside look')

    if type == 'exact':
        print('type was exact')
        #go through all the packages returned from database
        for package in packages_json:
            print('current package',package,'checking against',version,name)
            #if the package matches the query
            if((package['Version'] == version) and (package['Name'] == name)):
                print('match')
                #format and return 
                return_list.append(package)

                counter += 1

                #if there were more than 1000 packages that match, return 413
                if(counter > 1000):
                    return "Too many packages matched that query (> 1000)", 413
                
    if type == 'range':
        print('type was range')
        print(version)
        lower = version[0].replace('.', ', ')
        upper = version[1].replace('.', ', ')
        lower_tup = tuple(map(int, lower.split(', ')))
        upper_tup = tuple(map(int, upper.split(', ')))
       

        #go through all the packages returned from database
        for package in packages_json:
            print('current package',package,'checking against',lower_tup,upper_tup)
            package_tup = tuple(map(int, package['Version'].split('.')))

            #if the package matches the query
            if((package_tup >= lower_tup) and (package_tup <= upper_tup) and (package['Name'] == name)):
                print('match')
                
                #format and return 
                return_list.append(package)

                counter += 1

                #if there were more than 1000 packages that match, return 413
                if(counter > 1000):
                    return "Too many packages matched that query (> 1000)", 413
                
    if type == 'carrot':
        print('type was carrot/caret')
        lower = version.replace('.', ', ')
        lower_tup = tuple(map(int, lower.split(', ')))

        #go through all the packages returned from database
        for package in packages_json:
            print('current package',package,'checking against',name,lower_tup)

            package_tup = tuple(map(int, package['Version'].split('.')))
            
            #if the package matches the query
            if((package_tup >= lower_tup) and (package['Name'] == name)):
                print('match')
                
                #format and return 
                return_list.append(package)

                counter += 1

                #if there were more than 1000 packages that match, return 413
                if(counter > 1000):
                    return "Too many packages matched that query (> 1000)", 413
                
    if type == 'tilde':

        upper = version.replace('.', ', ')
        upper_tup = tuple(map(int, upper.split(', ')))
        orig_tup = upper_tup
        upper_tup[1] = str(int(upper_tup[1]) + 1)
        upper_tup[2] = '0'
        print('type was tilde')

        #go through all the packages returned from database
        for package in packages_json:
            print('current package',package,'checking against',package_tup,orig_tup,upper_tup,name)

            package_tup = tuple(map(int, package['Version'].split('.')))

            #if the package matches the query
            if((package_tup >= orig_tup) and (package_tup <= upper_tup) and (package['Name'] == name)):
                print('match')
                
                #format and return 
                return_list.append(package)

                counter += 1

                #if there were more than 1000 packages that match, return 413
                if(counter > 1000):
                    return "Too many packages matched that query (> 1000)", 413
    print(return_list)
    return return_list



def search_packages(request):

    #request has name and version
    request_content = json.loads(request)
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
            print('ending carrot')
        
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
    
    #turn the list of packages into json and return it
    return_json = json.dumps(return_list)
    
    print("packages found that match query: "+ str(return_list))

    return return_json, 200

json_test = [{ "Version": "1.36.2","Name": "cloudinary" },{ "Version": "^1.2.3","Name": "cloudinary" },{ "Version": "1.2.3-2.3.4","Name": "cloudinary" },{ "Version": "^1.2.3","Name": "cloudinary" },{ "Version": "~1.3.1","Name": "cloudinary" }]

print(search_packages(json.dumps(json_test)))