import axios from 'axios'

const client = axios.create({
  baseURL: process.env.REACT_APP_API_END_POINT,
  timeout: 30000
  // headers: {
  //   'Api-Auth-Token': ''
  // }
})

export default client
