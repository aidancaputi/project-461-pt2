import requests
import json

def main():

    example_body = '{"metadata": {"Name": "string","Version": "1.2.3","ID": "string"},"data": { "Content": "string","URL": "string","JSProgram": "string"}}'
    example_json = json.loads(example_body)

    print(example_json['metadata']['Name'])



    try:
        post_pkgs = requests.post('http://localhost:8080/packages')
        print('post /packages content',post_pkgs.json())
        print('post /packages status',post_pkgs.status_code)

    except:
        print('post /packages failed')

    addSpace()

    try:
        reset = requests.delete('http://localhost:8080/reset')
        print('delete /reset content',reset.json())
    except:
        print('delete /reset failed')

    addSpace()
    
    try:
        get_id = requests.get('http://localhost:8080/package/lodash')
        print('get package/<id> status',get_id.status_code)
        print('get package/<id>',post_pkgs.json())

    except:
        print('get package/<id> failed')

    addSpace()
    
    try:
        put_id = requests.put('http://localhost:8080/package/lodash')
    except:
        print('put package/<id> failed')

    addSpace()

    try:
        delete_id = requests.delete('http://localhost:8080/package/lodash')
    except:
        print('delete package/<id> failed')

    addSpace()

    try:
        post_pkg = requests.post('http://localhost:8080/package')
    except:
        print('post package failed')

    addSpace()

    try:
        get_id_rate = requests.get('http://localhost:8080/package/lodash/rate')
    except:
        print('get package/<id>/rate failed')

    addSpace()

    try:
        authenticate = requests.put('http://localhost:8080/authenticate')
    except:
        print('put authenticate failed')

    addSpace()

    try:
        get_pkg_byName = requests.post('http://localhost:8080/package/byName/lodash')
    except:
        print('get package/byName/<name> failed')

    addSpace()

    try:
        del_pkg_byName = requests.delete('http://localhost:8080/package/byName/lodash')
    except:
        print('delete package/byName/<name> failed')


    #post_pkg_byRegEx = requests.post('http://localhost:8080/package/byRegEx')

def addSpace():
    print('')
    pass







    




main()