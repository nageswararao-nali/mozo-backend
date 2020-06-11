def codes(code, message):
    if code == 200:
        response_200 = {
            "statusCode": 200,
            "data": message
        }
        return response_200
    elif code == 400:
        response_400 = {
            "statusCode": 400,
            "data": message
        }
        return response_400
    elif code == 404:
        response_404 = {
            "statusCode": 404,
            "data": message
        }
        return response_404
    elif code == 406:
        response_406 = {
            "statusCode": 406,
            "data": message
        }
        return response_406
