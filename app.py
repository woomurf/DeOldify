import os
import sys
import requests
import ssl
from flask import Flask, redirect, url_for, request
from flask import request
from flask import jsonify
from flask import send_file


from app_utils import download, DownloadPrecheckFailed
from app_utils import generate_random_filename
from app_utils import clean_me
from app_utils import clean_all
from app_utils import create_directory
from app_utils import get_model_bin
from app_utils import convertToJPG

from os import path
import torch

import fastai
from deoldify.visualize import *
from pathlib import Path
import traceback


torch.backends.cudnn.benchmark=True

#os.environ['CUDA_VISIBLE_DEVICES']='0'

app = Flask(__name__)


# define a predict function as an endpoint
@app.route("/process-img", methods=["POST"])
def process_image():
    input_path = generate_random_filename(upload_directory,"jpeg")
    output_path = os.path.join(results_img_directory, os.path.basename(input_path))

    try:
        url = request.json["source_url"]
        render_factor = 35 #int(request.json["render_factor"])

        download(url, input_path)

        try:
            image_colorizer.plot_transformed_image(path=input_path, figsize=(20,20),
            render_factor=render_factor, display_render_factor=True, compare=False)
        except:
            convertToJPG(input_path)
            image_colorizer.plot_transformed_image(path=input_path, figsize=(20,20),
            render_factor=render_factor, display_render_factor=True, compare=False)

        callback = send_file(output_path, mimetype='image/jpeg')
        
        return callback, 200

    except DownloadPrecheckFailed as e:
        return jsonify({'message': str(e)}), 500
    except:
        traceback.print_exc()
        return jsonify({'message': 'input error'}), 400

    finally:
        pass
        clean_all([
            input_path,
            output_path
            ])

@app.route('/health')
def health():
    return "ok"

@app.route('/')
def main():
    return """
    <head>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
    integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    </head>
    <div class=container>
    <div class="jumbotron mt-3">
    <h1>ainized-DeOldify</h1>
    <A>Git hub repository : </A> <A href="https://bit.ly/39xp9db"> DeOldify </A> <br>
    <A>API deployed on  </A> <A href="http://bit.ly/390JkQr"> Ainize </A>
    <hr class="my-4">
    <h3>Image URL: <input id="source_url" placeholder="http://"> </h3><br>
    <style>
    #submit{
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        border-bottom-left-radius: 5px;
        border-bottom-right-radius: 5px;
    }
    </style>
    <div>
        <h2>Select type!</h2>
        <input type="radio" name="type" id="option" value="picture"> Picture <br>
        <input type="radio" name="type" id="option" value="anime"> Animation <br>
    </div>
    <h3>RUN:  <button type="submit" class="btn btn-primary btn-lg" id="submit">Submit</button></h3>
    <div id="result">
        <image id="resultImage">
    </div>
    <script>
    const run = (retry_cnt=0, retry_sec=1,) => {
        if (retry_cnt < 3) {
            retry_cnt += 1
            retry_sec *= 2
        } else {
            throw Error('Retry Error');
        }
        checked=document.querySelector('input[name="type"]:checked').value;
        if (checked=='anime'){
            url = "https://deoldify-api-ani.kmswlee.endpoint.ainize.ai/process-img-ani"
            data = JSON.stringify({
            source_url: document.getElementById('source_url').value,
            render_factor: 26,
            })
        }
        else{
            url = "/process-img"
            data = JSON.stringify({
            source_url: document.getElementById('source_url').value,
            render_factor: 35,
            })
        }

        fetch(url, {method:'POST', headers: {'Content-Type': 'application/json'}, body: data})
            .then(response => {
                if (response.status === 200) {
                    return response;
                } else if (response.status === 429) {
                    console.log(`retry ${retry_cnt}th after ${retry_sec}secs ...`);
                    setTimeout(
                        () => {
                            run(retry_cnt, retry_sec)
                        }, retry_sec * 1000
                    )
                } else {
                    throw Error('Server Error - Debugging Please!');
                }
            })
            .then(response => response.blob())
            .then(blob => URL.createObjectURL(blob))
            .then(imageURL => {
                document.getElementById('result').style.display = 'block';
                document.getElementById('resultImage').src = imageURL;
            })
    };

    document.getElementById('submit').onclick = () => run()    
    </script>
    </div>
    </div>
"""

if __name__ == '__main__':
    global upload_directory
    global results_img_directory
    global image_colorizer
    #global video_colorizer

    upload_directory = '/data/upload/'
    #create_directory(upload_directory)

    results_img_directory = '/data/result_images/'
    #create_directory(results_img_directory)

    model_directory = '/data/models/'
    #create_directory(model_directory)

    #artistic_model_url = 'https://www.dropbox.com/s/zkehq1uwahhbc2o/ColorizeArtistic_gen.pth?dl=0'
    #get_model_bin(artistic_model_url, os.path.join(model_directory, 'ColorizeArtistic_gen.pth'))

    image_colorizer = get_image_colorizer(artistic=True)


    print('ready for')
    app.run(host='0.0.0.0', port=80, threaded=False)

