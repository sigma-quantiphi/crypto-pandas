def prepare_requests_parameters(params: dict) -> dict:
    params = {k: v for k, v in params.items() if v is not None}
    for x in ["startTime", "endTime", "transferDate"]:
        if x in params:
            params[x] = int(params[x].timestamp() * 1000)
        return params
