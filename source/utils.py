import json

def get_list(file):
    if not file:
        print("No Params (file:str)")
        return None

    ret = []
    try:
        with open(file,"r") as f:
            for aa in f:
                ret.append(aa.strip())
    except Exception as e:
        print(f"error_from_utils.get_list() : {e}")
    return ret

def write_to_json(file, data):
    if not file or not data:
        print("No Params (file:str, data:Dict)")
        return None

    with open(file, "w") as f:
        f.write(json.dumps(data))
    print(f"WRITE TO [{file}] COMPLETE.")

def read_to_json(file):
    if not file:
        print("No Params (file:str)")
        return None

    with open(file, "r") as f:
        data = json.load(f)
    return data

def saving_log(file, log):
    if not file or not log:
        print("No Params (file:str, log:str)")
        return None

    with open(file, "w") as f:
        f.write(log)
    print(f"SAVING_LOG [{file}] COMPLETE.")



if __name__=="__main__":
    pass
    # print(get_list("../secret/asdf.txt"))
    # print(get_list("../secret/hashtags.txt"))

