import axios from 'axios'

const request = axios.create({
    baseURL: 'http://10.254.47.34:8000', // url = base url + request url
    // send cookies when cross-domain requests
    timeout: 5000 // request timeout
});

export default request;