from fastapi import FastAPI

app = FastAPI()

@app.get("/queryparameters")
def query_parameters(param1: str = None, param2: int = None) -> dict:

    

    namen = ["martin", "sophia", "michael", "emma", "maria", "matthias"]

    if not param1:
        return
             
    namen_gefiltert = []
    for name in namen:
        if param1 in name:
            namen_gefiltert.append(name)

    return {
        "param1": param1,
        "param2": param2

    }