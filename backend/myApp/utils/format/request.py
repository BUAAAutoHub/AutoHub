DEFAULT_ERR_CODE = 1

def getResp(errcode  =DEFAULT_ERR_CODE, message="404 not success"):
    response = {'errcode': errcode  , 'message': message}
    return response