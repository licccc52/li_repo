const WS_HOST = process.env.REACT_APP_WEB_SOCKET_END_POINT
export default WS_HOST

export const CHAT_HOST = WS_HOST + '/chat'