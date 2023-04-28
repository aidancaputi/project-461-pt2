import requests
import json
import base64
import traceback

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
        put_authenticate = requests.put('http://localhost:8080/authenticate', json=put_authenticate_req)
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
            "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
        }
        post_pkg_url_resp = requests.post('http://localhost:8080/package', json=post_pkg_url)
        print('\nPOST PKG 1 RESPONSE CODE: ',str(post_pkg_url_resp.status_code),' ',str(post_pkg_url_resp.content),'\n')
        count += 1
    except:
        failed_tests.append('POST PKG URL 1')
        traceback.print_exc()
        print("post /package URL 1 failed with code above")

    # #put /package/id-- come back to this one
    # try:    
    #     put_package_id = {
    #         "metadata": {
    #             "Name": "cloudinary",
    #             "Version": "1.2.3",
    #             "ID": "tbd"
    #         },
    #         "data": {
    #             "Content": str(encoded_cloudinary),
    #             "URL": "https://github.com/cloudinary/cloudinary_npm",
    #             "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
    #         }
    #     }
    #     put_package_id_resp = requests.put('http://localhost:8080/package/id', json=put_package_id)
    #     print('\nPUT PKG ID RESPONSE CODE: ',str(put_package_id_resp.status_code),' ',str(put_package_id_resp.content),'\n')
        
    #     count += 1
    # except:
    #     failed_tests.append('PUT PKG ID')
    #     traceback.print_exc()
    #     print("put /package/id failed with code above")

    # #get /package/id
    # try:
    #     get_package_id_resp = requests.get('http://localhost:8080/package/tbd')
    #     print('\nGET PKG ID RESPONSE CODE: ',str(get_package_id_resp.status_code),' ',str(get_package_id_resp.content),'\n')

    #     count += 1
    # except:
    #     failed_tests.append('GET PKG ID')
    #     traceback.print_exc()
    #     print("get pkg/id failed with code above")

    # #get /package/id/rate
    # try:
    #     get_package_id_rate_resp = requests.get('http://localhost:8080/package/tbd/rate')
    #     print('\nGET PKG ID RATE RESPONSE CODE: ',str(get_package_id_rate_resp.status_code),' ',str(get_package_id_rate_resp.content),'\n')

    #     count += 1
    # except:
    #     failed_tests.append('GET PKG ID RATE')
    #     traceback.print_exc()
    #     print("get /package/id/rate failed with code above")

    # #post /package - base64 SECOND
    # try:
    #     post_pkg_base642 = {
    #         "Content": str(encoded_axios),
    #         "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
    #     }
    #     post_pkg_base64_resp2 = requests.post('http://localhost:8080/package', json=post_pkg_base642)
    #     print('\nPOST PKG B64 AXIOS RESPONSE CODE: ',str(post_pkg_base64_resp2.status_code),' ',str(post_pkg_base64_resp2.content),'\n')

    #     count += 1
    # except:
    #     failed_tests.append('POST PKG BASE64 AXIOS')
    #     traceback.print_exc()
    #     print("post /package base64 axios failed with code above")

    # #post /packages
    # try:
    #     post_pkgs = requests.post('http://localhost:8080/packages', json={ "Version": "Exact (1.2.3)\nBounded range (1.2.3-2.1.0)\nCarat (^1.2.3)\nTilde (~1.2.0)", "Name": "cloudinary" })
    #     print('\nPOST PKGS RESPONSE CODE: ',str(post_pkgs.status_code),' ',str(post_pkgs.content),'\n')

    #     count += 1

    # except:
    #     failed_tests.append('POST PKGS')
    #     traceback.print_exc()
    #     print('post /packages failed with status above')

    # #get /package/byname/name
    # try:
    #     get_package_name_resp = requests.get('http://localhost:8080/package/byName/axios')
    #     print('\nGET PKG BYNAME RESPONSE CODE: ',str(get_package_name_resp.status_code),' ',str(get_package_name_resp.content),'\n')

    #     count += 1
    # except:
    #     failed_tests.append('GET PKG BYNAME')
    #     traceback.print_exc()
    #     print("get /package/byName failed with code above")
    
    # #delete /package/byname/name
    # try:
    #     delete_package_name_resp = requests.delete('http://localhost:8080/package/byName/cloudinary')
    #     print('\nDEL PKG BYNAME RESPONSE CODE: ',str(delete_package_name_resp.status_code),' ',str(delete_package_name_resp.content),'\n')

    #     count += 1
    # except:
    #     failed_tests.append('DELETE PKG BYNAME')
    #     traceback.print_exc()
    #     print("delete /package/byName failed with code above")

    # #delete /package/id
    # try:
    #     delete_package_id_resp = requests.delete('http://localhost:8080/package/tbd')
    #     print('\nDEL PKG BY ID RESPONSE CODE: ',str(delete_package_id_resp.status_code),' ',str(delete_package_id_resp.content),'\n')

    #     count += 1
    # except:
    #     failed_tests.append('DEL PKG ID')
    #     traceback.print_exc()
    #     print("delete /package/id failed with code above")

    # #post /package - URL
    # try:
    #     post_pkg_url2 = {
    #         "URL": 'https://github.com/moleculerjs/moleculer',
    #         "JSProgram": "if (process.argv.length === 7) {\nconsole.log('Success')\nprocess.exit(0)\n} else {\nconsole.log('Failed')\nprocess.exit(1)\n}\n"
    #     }
    #     post_pkg_url_resp2 = requests.post('http://localhost:8080/package', json=post_pkg_url2)
    #     print('\nPOST PKG URL2 RESPONSE CODE: ',str(post_pkg_url_resp2.status_code),' ',str(post_pkg_url_resp2.content),'\n')

    #     count += 1
    # except:
    #     failed_tests.append('POST PKG URL 2')
    #     traceback.print_exc()
    #     print("post /package URL 2 failed with code above")
    
    #delete /reset
    # try:
    #     delete_reset_resp = requests.delete('http://localhost:8080/reset')
    #     print('\nDELETE RESET RESPONSE CODE: ',str(delete_reset_resp.status_code),' ',str(delete_reset_resp.content),'\n')

    #     count += 1
    # except:
    #     failed_tests.append('DELETE RESET')
    #     traceback.print_exc()
    #     print("delete /reset failed with code above")

    print("passed: " + str(count) + " | failed: " + str(12 - count))
    print(f'score: {str(count)} / 12 -> {str(round(100*count/12,2))} %')
    print('Failed tests:')
    for f in failed_tests:
        print(f)

main()