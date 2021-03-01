from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd


app = Flask(__name__)


CORS(app)


@app.route('/', methods=['GET'])
def chain_arr_ui():
    return "<h1>hey from the home page</h1>"


@app.route('/chainage_av', methods=['GET'])
def chain_av_ui():
    return send_from_directory('ui', 'chainage_avant.html')


@app.route("/test", methods=['POST'])
def test_():
    file = request.files['regles']
    print(file)
    response = {
        "message": "hey from file"
    }
    return jsonify(response), 200


@app.route("/chainage_av", methods=['POST'])
def chainage_av():
    file = request.files['regles']
    data = pd.read_csv(file, sep=";", header=None, names=["Les regles"])
    # from the request :
    values = request.form
    BF = values["BF"].split(',')
    element = values["EL"]

    # Creating the data from the csv file
    tab = []
    for i in range(len(data)):
        case = {
            "Prémisse": data.iloc[i][0].split("(")[1].split(")")[0].split(","),
            "Actions": data.iloc[i][0].split("(")[2].split(")")[0].split(","),
            "Used": False
        }
        tab.append(case)
    used_count = 0

    while True:
        if(used_count == len(tab)):
            # returning the response with the err message
            response = {
                "message": "un bloquage est survenu",
                "base_de_fait":BF,
                "regles":tab
            }
            return jsonify(response), 202
            break
        if (element in BF):
            nvl_list = [{"si": element['Prémisse'], "alors":element["Actions"]}
                        for element in tab if(element["Used"])]
            response = {
                'message': f"l'element {element} est dans la base de fait",
                "base_de_fait": BF,
                "regles": tab,
            }
            return jsonify(response), 200
            break
        else:
            for i in range(len(tab)):
                if (tab[i]["Used"]):
                    used_count += 1
                    continue
                else:
                    if (all([el in BF for el in tab[i]["Prémisse"]])):
                        used_count = 0
                        # [BF.append(el) for el in tab[i]["Actions"]]
                        BF = BF + tab[i]["Actions"]
                        tab[i]["Used"] = True
                        break
                    elif (i == (len(tab)-1)):
                        used_count = len(tab)
                        break


@app.route("/chainage_arr", methods=['POST'])
def chainage_arr():
    file = request.files['regles']
    data = pd.read_csv(file, sep=";", header=None, names=["Les regles"])
    values = request.form
    BF = values["BF"].split(",")
    element = values["EL"]
    # Creating the data from the csv file
    tab = []
    for i in range(len(data)):
        case = {
            "Prémisse": data.iloc[i][0].split("(")[1].split(")")[0].split(","),
            "Actions": data.iloc[i][0].split("(")[2].split(")")[0].split(","),
            "Used": False
        }
        tab.append(case)
    blockage = False
    prec = element
    while True:
        if (blockage):
            response = {
                "message": "Un bloquage est survenue.",
                "base_de_fait": BF,
                "regles" : tab

            }
            return jsonify(response), 202
            break
        element = values["EL"]
        if (element in BF):
            nvl_list = [{"si": element['Prémisse'], "alors":element["Actions"]}
                        for element in tab if(element["Used"])]
            response = {
                'message': f"l'element {element} est dans la base de fait",
                "base_de_fait": BF,
                "regles" : tab
            }
            return jsonify(response), 200
            break
        else:
            i = 0
            while i < len(tab):
                if (tab[i]["Used"]):
                    i += 1
                    continue
                else:
                    if ((element in tab[i]["Actions"])):
                        if(all([el in BF for el in tab[i]["Prémisse"]])):
                            BF = BF + tab[i]['Actions']
                            tab[i]['Used'] = True
                            prec = ''
                            break
                        else:
                            for j in range(len(tab[i]["Prémisse"])):
                                if (tab[i]["Prémisse"][j] not in BF):
                                    prec = element
                                    element = tab[i]["Prémisse"][j]
                                    i = 0
                                    break
                    else:
                        if(i == (len(tab)-1)):
                            if(element == prec):
                                blockage = True
                                break
                            element = prec
                            for i in range(len(tab)):
                                if (element in tab[i]['Actions']):
                                    tab[i]['Used'] = True
                                    i = 0
                                    break
                        i += 1


if __name__ == '__main__':
    app.run()

