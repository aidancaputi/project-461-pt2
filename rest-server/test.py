import requests
import json
import base64
import traceback
import zipfile

def main():
    failed_tests = []
    #example_body = '{"metadata": {"Name": "string","Version": "1.2.3","ID": "string"},"data": { "Content": "string","URL": "string","JSProgram": "string"}}'
    #example_body = '{ "Version": "Exact (1.2.3)\nBounded range (1.2.3-2.1.0)\nCarat (^1.2.3)\nTilde (~1.2.0)", "Name": "string" }'
    #example_json = json.dumps(example_body)

    #encode the zip for content
    with open("test_zips/cloudinary_npm-master.zip", "rb") as file1:
        encoded_cloudinary = base64.b64encode(file1.read())
    with open("test_zips/axios-1.x.zip", "rb") as file2:
        encoded_axios = base64.b64encode(file2.read())

    count = 0

    #put /authenticate
    #post /package
    #put /package/id X
    #get /package/id X
    #get /package/id/rate
    #post second /package
    #post /packages
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
        put_authenticate = requests.put('https://rest-server-h5si5ezrea-uc.a.run.app/authenticate', json=put_authenticate_req)
        print('\nPUT_AUTHENTICATE RESPONSE CODE: ',str(put_authenticate.status_code),' ',str(put_authenticate.content),'\n')
        count += 1
    except:
        failed_tests.append('PUT AUTHENTICATE')
        traceback.print_exc()
        print('put /authenticate failed with code above')


    #post /package - URL
    try:
        post_pkg_url = {
            "URL": 'https://github.com/cloudinary/cloudinary_npm',
            "Content" : None,
            "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
        }
        post_pkg_url_resp = requests.post('https://rest-server-h5si5ezrea-uc.a.run.app/package', json=post_pkg_url)

        post_pkg_url_resp_json = json.loads(post_pkg_url_resp.content)
        print('\nPOST PKG 1 RESPONSE CODE: ',str(post_pkg_url_resp.status_code),' ',str(len(post_pkg_url_resp_json['data']['Content'])),'\n')
        count += 1
        cloudinary_id = post_pkg_url_resp_json['metadata']['ID']
        cloudinary_ver = post_pkg_url_resp_json['metadata']['Version']
    except:
        failed_tests.append('POST PKG URL 1')
        traceback.print_exc()
        print("post /package URL 1 failed with code above")

    #put /package/id-- come back to this one
    try:    
        put_package_id = {
            "metadata": {
                "Name": "cloudinary",
                "Version": cloudinary_ver,
                "ID": cloudinary_id
            },
            "data": {
                "Content": str(encoded_cloudinary)[2:],
                "URL": "https://github.com/cloudinary/cloudinary_npm",
                "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success 2')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
            }
        }
        put_package_id_resp = requests.put('https://rest-server-h5si5ezrea-uc.a.run.app/package/cloudinary', json=put_package_id)
        print('\nPUT PKG ID RESPONSE CODE: ',str(put_package_id_resp.status_code),' ',str(put_package_id_resp.content),'\n')
        count += 1
    except:
        failed_tests.append('PUT PKG ID')
        traceback.print_exc()
        print("put /package/id failed with code above")
    
    #put /package/id-- come back to this one -> should fail
    try:    
        put_package_id = {
            "metadata": {
                "Name": "cloudinary",
                "Version": cloudinary_ver,
                "ID": 'askdjhfka'
            },
            "data": {
                "Content": str(encoded_cloudinary)[2:],
                "URL": "https://github.com/cloudinary/cloudinary_npm",
                "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success 2')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
            }
        }
        put_package_id_resp = requests.put('https://rest-server-h5si5ezrea-uc.a.run.app/package/cloudinaryaaa', json=put_package_id)
        print('\nPUT PKG ID RESPONSE CODE: ',str(put_package_id_resp.status_code),' ',str(put_package_id_resp.content),'\n')
        count += 1
    except:
        failed_tests.append('PUT PKG ID')
        traceback.print_exc()
        print("put /package/id failed with code above")

    #get /package/id
    try:
        get_package_id_resp = requests.get(f'https://rest-server-h5si5ezrea-uc.a.run.app/package/{cloudinary_id}')
        get_package_id_resp_json = json.loads(get_package_id_resp.content)
        print('\nGET PKG ID RESPONSE CODE: ',str(get_package_id_resp.status_code),' ',str(len(get_package_id_resp_json['data']['Content'])),'\n')
        count += 1
    except:
        failed_tests.append('GET PKG ID')
        traceback.print_exc()
        print("get pkg/id failed with code above")
    
    #get /package/id -> should return 404
    try:
        get_package_id_resp = requests.get(f'https://rest-server-h5si5ezrea-uc.a.run.app/package/klhaefa')
        print('\nGET PKG ID RESPONSE CODE: ',str(get_package_id_resp.status_code))
        count += 1
    except:
        failed_tests.append('GET PKG ID')
        traceback.print_exc()
        print("get pkg/id failed with code above")

    #get /package/id/rate
    try:
        get_package_id_rate_resp = requests.get(f'https://rest-server-h5si5ezrea-uc.a.run.app/package/{cloudinary_id}/rate')
        print('\nGET PKG ID RATE RESPONSE CODE: ',str(get_package_id_rate_resp.status_code),' ',str(get_package_id_rate_resp.content),'\n')

        count += 1
    except:
        failed_tests.append('GET PKG ID RATE')
        traceback.print_exc()
        print("get /package/id/rate failed with code above")

     #get /package/id/rate -> should fail
    try:
        get_package_id_rate_resp = requests.get(f'https://rest-server-h5si5ezrea-uc.a.run.app/package/cloudinaryarqaefa/rate')
        print('\nGET PKG ID RATE RESPONSE CODE: ',str(get_package_id_rate_resp.status_code),' ',str(get_package_id_rate_resp.content),'\n')

        count += 1
    except:
        failed_tests.append('GET PKG ID RATE')
        traceback.print_exc()
        print("get /package/id/rate failed with code above")

    #post /package - base64 SECOND
    try:
        post_pkg_base642 = {
            "Content": str(encoded_axios)[2:],
            "URL" : None,
            "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
        }
        post_pkg_base64_resp2 = requests.post('https://rest-server-h5si5ezrea-uc.a.run.app/package', json=post_pkg_base642)
        post_pkg_base64_resp2_json = json.loads(post_pkg_base64_resp2.content)
        print('\nPOST PKG B64 AXIOS RESPONSE CODE: ',str(post_pkg_base64_resp2.status_code),' ',str(len(post_pkg_base64_resp2_json['data']['Content'])),'\n')

        count += 1
    except:
        failed_tests.append('POST PKG BASE64 AXIOS')
        traceback.print_exc()
        print("post /package base64 axios failed with code above")

    print('cloud',cloudinary_ver)
    #post /packages
    pkgs_json = [{ "Version": f"{cloudinary_ver})","Name": "cloudinary" },{ "Version": "^1.2.3","Name": "cloudinary" },{ "Version": "1.2.3-2.3.4","Name": "cloudinary" },{ "Version": "^1.2.3","Name": "cloudinary" },{ "Version": "~1.2.3","Name": "cloudinary" }]
    try:
        post_pkgs = requests.post('https://rest-server-h5si5ezrea-uc.a.run.app/packages', json=pkgs_json)
        print('\nPOST PKGS RESPONSE CODE: ',str(post_pkgs.status_code),' ',str(post_pkgs.content),'\n')

        count += 1

    except:
        failed_tests.append('POST PKGS')
        traceback.print_exc()
        print('post /packages failed with status above')

    #get /package/byname/name
    try:
        get_package_name_resp = requests.get('https://rest-server-h5si5ezrea-uc.a.run.app/package/byName/axios')
        print('\nGET PKG BYNAME RESPONSE CODE: ',str(get_package_name_resp.status_code),' ',str(get_package_name_resp.content),'\n')

        count += 1
    except:
        failed_tests.append('GET PKG BYNAME')
        traceback.print_exc()
        print("get /package/byName failed with code above")

    #get /package/byname/name -> should return 404
    try:
        get_package_name_resp = requests.get('https://rest-server-h5si5ezrea-uc.a.run.app/package/byName/axiosssss')
        print('\nGET PKG BYNAME RESPONSE CODE: ',str(get_package_name_resp.status_code),' ',str(get_package_name_resp.content),'\n')

        count += 1
    except:
        failed_tests.append('GET PKG BYNAME')
        traceback.print_exc()
        print("get /package/byName failed with code above")
    
    #delete /package/byname/name
    try:
        delete_package_name_resp = requests.delete('https://rest-server-h5si5ezrea-uc.a.run.app/package/byName/axios')
        print('\nDEL PKG BYNAME RESPONSE CODE: ',str(delete_package_name_resp.status_code),' ',str(delete_package_name_resp.content),'\n')

        count += 1
    except:
        failed_tests.append('DELETE PKG BYNAME')
        traceback.print_exc()
        print("delete /package/byName failed with code above")
    
     #delete /package/byname/name -> should return 404
    try:
        delete_package_name_resp = requests.delete('https://rest-server-h5si5ezrea-uc.a.run.app/package/byName/axiosssss')
        print('\nDEL PKG BYNAME RESPONSE CODE: ',str(delete_package_name_resp.status_code),' ',str(delete_package_name_resp.content),'\n')

        count += 1
    except:
        failed_tests.append('DELETE PKG BYNAME')
        traceback.print_exc()
        print("delete /package/byName failed with code above")

    #delete /package/id
    try:
        delete_package_id_resp = requests.delete(f'https://rest-server-h5si5ezrea-uc.a.run.app/package/{cloudinary_id}')
        print('\nDEL PKG BY ID RESPONSE CODE: ',str(delete_package_id_resp.status_code),' ',str(delete_package_id_resp.content),'\n')

        count += 1
    except:
        failed_tests.append('DEL PKG ID')
        traceback.print_exc()
        print("delete /package/id failed with code above")
    
    #delete /package/id -> should return 404
    try:
        delete_package_id_resp = requests.delete(f'https://rest-server-h5si5ezrea-uc.a.run.app/package/{cloudinary_id}')
        print('\nDEL PKG BY ID RESPONSE CODE: ',str(delete_package_id_resp.status_code),' ',str(delete_package_id_resp.content),'\n')

        count += 1
    except:
        failed_tests.append('DEL PKG ID')
        traceback.print_exc()
        print("delete /package/id failed with code above")

    #post /package - URL
    try:
        post_pkg_url2 = {
            "Content" : None,
            "URL": 'https://github.com/moleculerjs/moleculer',
            "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
        }
        post_pkg_url_resp2 = requests.post('https://rest-server-h5si5ezrea-uc.a.run.app/package', json=post_pkg_url2)
        post_pkg_url_resp2_json = json.loads(post_pkg_url_resp2.content)
        print('\nPOST PKG URL2 RESPONSE CODE: ',str(post_pkg_url_resp2.status_code),' ',str(len(post_pkg_url_resp2_json['data']['Content'])),'\n')

        count += 1
    except:
        failed_tests.append('POST PKG URL 2')
        traceback.print_exc()
        print("post /package URL 2 failed with code above")
    
    #post regex
    reg_json = {
        "RegEx" : "a*"
    }

    try:
        reg_resp = requests.post('https://rest-server-h5si5ezrea-uc.a.run.app/package/byRegEx',json=reg_json)
        print('\nREGEX RESET RESPONSE CODE: ',str(reg_resp.status_code),' ',str(reg_resp.content),'\n')

        count += 1
    except:
        failed_tests.append('DELETE RESET')
        traceback.print_exc()
        print("delete /reset failed with code above")
    
    #delete /reset
    try:
        delete_reset_resp = requests.delete('https://rest-server-h5si5ezrea-uc.a.run.app/reset')
        print('\nDELETE RESET RESPONSE CODE: ',str(delete_reset_resp.status_code),' ',str(delete_reset_resp.content),'\n')

        count += 1
    except:
        failed_tests.append('DELETE RESET')
        traceback.print_exc()
        print("delete /reset failed with code above")

    tot = 19
    print("passed: " + str(count) + " | failed: " + str(tot - count))
    print(f'score: {str(count)} / {str(tot)} -> {str(round(100*count/tot,2))} %')
    print('Failed tests:')
    for f in failed_tests:
        print(f)

main()