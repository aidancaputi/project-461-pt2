# httprequest

[![latest version published to npm](https://badge.fury.io/js/httprequest.svg)](https://www.npmjs.com/package/httprequest)

[XMLHttpRequest](http://www.w3.org/TR/XMLHttpRequest/) wrapper.

```sh
npm install httprequest
```


### Example

```javascript
import {Request} from 'httprequest'

new Request('POST', '/api/reservations')
.sendData({venue_id: 100}, (err, response) => {
  if (err) throw err
  console.log('got response', res)
})
```


## License

Copyright 2015–2018 Christopher Brown.
[MIT Licensed](https://chbrown.github.io/licenses/MIT/#2015-2018).
