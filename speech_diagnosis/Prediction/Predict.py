from tensorflow.keras.models import load_model
from tensorflow.keras.models import model_from_json
import json
import numpy as np
import pickle
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class Predict:


    location = {
        "NN": {"weights": "..//ML_Models//NN//Speech_nn.h5", "architecture": "..//ML_Models//NN//model_nn.json",
               "Scalar": "..//ML_Models//NN//scalar.pkl"},
        "KNN": "",
        "RF": "",
        "SVC": ""
    }


    def __init__(self,model_name="NN"):

        self.model_name = model_name
        self.model = None
        self.scalar = None
        self.model_load_success = self.load_model_from_files(self.location[self.model_name])



    def load_model_from_files(self, model_location):

        try:

            with open(model_location["architecture"]) as json_file:
                loaded_model_json =  json_file.read()

            self.model = model_from_json(loaded_model_json)
            self.model.load_weights(model_location["weights"])

            with open(model_location["Scalar"], "rb") as scalar_file:
                self.scalar = pickle.load(scalar_file)

        except Exception as e:
            print(e)
            return False

        return True


    def clean_input(self, data):
        l=len(data.shape)

        if l==2:
            if not data.shape == (1,26):
                raise Exception("The dimensions of parameter do not match")
        elif l==1 :
            data = data.to_numpy().reshape(1, 26)
        else:
            raise Exception("The dimensions of parameter do not match")
        return data


    def scale_input(self, input):
        input = self.scalar.transform(input)
        return input


    def get_prediction(self, data):

        if not self.model_load_success:
            raise Exception("Model did not load successfully")

        data = np.array(data)

        try:
            input = self.clean_input(data)
            input= self.scale_input(input)
        except Exception as e:
            raise e

        prediction = self.model.predict(input).reshape(1,)[0]

        predictions_rounded = np.round_(prediction)

        diagnosis = (1==predictions_rounded)

        return {"Diagnosis": diagnosis, "probability": float("{0:.2f}".format(prediction*100))}


    def get_PR_curve(self):
        pass

    def get_ROC_curve(self):
        pass

    def get_lime_analysis(self):
        pass




if __name__ == "__main__":

    predict = Predict("NN")
    data = [[1.488000e+00, 9.021300e-05, 9.000000e-01, 7.940000e-01,
        2.699000e+00, 8.334000e+00, 7.790000e-01, 4.517000e+00,
        4.609000e+00, 6.802000e+00, 1.355100e+01, 9.059050e-01,
        1.191160e-01, 1.113000e+01, 1.665330e+02, 1.647810e+02,
        1.042100e+01, 1.422290e+02, 1.875760e+02, 1.600000e+02,
        1.590000e+02, 6.064725e-03, 4.162760e-04, 0.000000e+00,
        0.000000e+00, 0.000000e+00]]

    res = predict.get_prediction(data)
    print(res)
