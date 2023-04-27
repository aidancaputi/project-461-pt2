import requests
import json
import base64

def main():

    #example_body = '{"metadata": {"Name": "string","Version": "1.2.3","ID": "string"},"data": { "Content": "string","URL": "string","JSProgram": "string"}}'
    #example_body = '{ "Version": "Exact (1.2.3)\nBounded range (1.2.3-2.1.0)\nCarat (^1.2.3)\nTilde (~1.2.0)", "Name": "string" }'
    #example_json = json.dumps(example_body)

    #encode the zip for content
    with open("test_zips/cloudinary_npm-master.zip", "rb") as file1:
        encoded_cloudinary = base64.b64encode(file1.read())
    with open("test_zips/axios-1.x.zip", "rb") as file2:
        encoded_axios = base64.b64encode(file2.read())

    count = 0

    #put /authenticate X
    #post /package X
    #put /package/id
    #get /package/id X
    #get /package/id/rate X
    #post second /package X
    #post /packages X
    #get /package/byname/name  X
    #post /package/regex
    #delete /package/byname/name X
    #delete /package/id X
    #post /package
    #delete /reset

    #put /authenticate
    try:
        put_authenticate_req = {
            "User": {
                "name": "ece30861defaultadminuser",
                "isAdmin": "true"
            },
            "Secret": {
                "password": "correcthorsebatterystaple123(!__+@**(A'\"`;DROP TABLE packages;"
            }
        }
        put_authenticate = requests.put('http://rest-server-h5si5ezrea-uc.a.run.app/authenticate', json=put_authenticate_req, verify=False)
        count += 1
    except:
        print("put /authenticate failed with code: " + str(put_authenticate.content))

    #post /package - URL
    try:
        post_pkg_url = {
            "URL": 'https://github.com/cloudinary/cloudinary_npm',
            "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
        }
        post_pkg_url_resp = requests.post('http://rest-server-h5si5ezrea-uc.a.run.app/package', json=post_pkg_url, verify=False)
        print("post /package URL succeed and got response: " + str(post_pkg_url_resp.content))
        count += 1
    except:
        print("post /package URL failed with code: " + str(post_pkg_url_resp.content))

    #put /package/id-- come back to this one
    try:    
        put_package_id = {
            "metadata": {
                "Name": "cloudinary",
                "Version": "1.2.3",
                "ID": "tbd"
            },
            "data": {
                "Content": encoded_cloudinary,
                "URL": "https://github.com/cloudinary/cloudinary_npm",
                "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
            }
        }
        put_package_id_resp = requests.put('http://rest-server-h5si5ezrea-uc.a.run.app/package/id', json=put_package_id, verify=False)
        
        count += 1
    except:
        print("put /package/id failed with code: " + str(put_package_id_resp.content))

    #get /package/id
    try:
        get_package_id_resp = requests.get('http://rest-server-h5si5ezrea-uc.a.run.app/package/tbd', verify=False)
        print("put /package/id succeeded with code: " + str(get_package_id_resp.content))
        count += 1
    except:
        print("put /package/id failed with code: " + str(get_package_id_resp.content))

    #get /package/id/rate
    try:
        get_package_id_rate_resp = requests.get('http://rest-server-h5si5ezrea-uc.a.run.app/package/tbd/rate', verify=False)
        print("put /package/id/rate succeeded with code: " + str(get_package_id_rate_resp.content))
        count += 1
    except:
        print("put /package/id/rate failed with code: " + str(get_package_id_resp.content))

    #post /package - base64 SECOND
    try:
        post_pkg_base642 = {
            "Content": encoded_axios,
            "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
        }
        post_pkg_base64_resp2 = requests.post('http://rest-server-h5si5ezrea-uc.a.run.app/package', json=post_pkg_base642, verify=False)
        print("post /package base64 2 succeed and got response: " + str(post_pkg_base64_resp2.content))
        count += 1
    except:
        print("post /package base64 2 failed with code: " + str(post_pkg_base64_resp2.content))

    #post /packages
    try:
        post_pkgs = requests.post('http://rest-server-h5si5ezrea-uc.a.run.app/packages', json={ "Version": "Exact (1.2.3)\nBounded range (1.2.3-2.1.0)\nCarat (^1.2.3)\nTilde (~1.2.0)", "Name": "cloudinary" })
        print('post /packages succeeded with status', str(post_pkgs.content))
        count += 1

    except:
        print('post /packages failed with status', str(post_pkgs.content))

    #get /package/byname/name
    try:
        get_package_name_resp = requests.get('http://rest-server-h5si5ezrea-uc.a.run.app/package/byName/axios', verify=False)
        print("get /package/byName succeeded with code: " + str(get_package_name_resp.content))
        count += 1
    except:
        print("put /package/byName failed with code: " + str(get_package_name_resp.content))
    
    #delete /package/byname/name
    try:
        delete_package_name_resp = requests.delete('http://rest-server-h5si5ezrea-uc.a.run.app/package/byName/cloudinary', verify=False)
        print("delete /package/byName succeeded with code: " + str(delete_package_name_resp.content))
        count += 1
    except:
        print("delete /package/byName failed with code: " + str(delete_package_name_resp.content))

    #delete /package/id
    try:
        delete_package_id_resp = requests.delete('http://rest-server-h5si5ezrea-uc.a.run.app/package/tbd', verify=False)
        print("delete /package/id succeeded with code: " + str(delete_package_id_resp.content))
        count += 1
    except:
        print("delete /package/id failed with code: " + str(delete_package_id_resp.content))

    #post /package - URL
    try:
        post_pkg_url3 = {
            "URL": 'https://github.com/moleculerjs/moleculer',
            "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
        }
        post_pkg_url_resp3 = requests.post('http://rest-server-h5si5ezrea-uc.a.run.app/package', json=post_pkg_url3, verify=False)
        print("post /package URL 3 succeed and got response: " + str(post_pkg_url_resp3.content))
        count += 1
    except:
        print("post /package URL 3 failed with code: " + str(post_pkg_url_resp3.content))
    
    #delete /reset
    try:
        delete_reset_resp = requests.delete('http://rest-server-h5si5ezrea-uc.a.run.app/reset', verify=False)
        print("delete /reset succeeded with code: " + str(delete_reset_resp.content))
        count += 1
    except:
        print("delete /reset failed with code: " + str(delete_reset_resp.content))

    print("passed: " + str(count) + " | failed: " + str(13 - count))

main()