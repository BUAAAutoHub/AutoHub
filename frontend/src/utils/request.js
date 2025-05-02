import axios from 'axios'

const request = axios.create({
    baseURL: 'http://127.0.0.1:8000', // url = base url + request url
    // send cookies when cross-domain requests
    timeout: 5000 // request timeout
});

export default request;