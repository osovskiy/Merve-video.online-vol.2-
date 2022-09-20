from random import randint
import os
import logging

from flask import render_template, url_for, request, jsonify, redirect, make_response
from flask_cors import cross_origin

from loader import app
from func import ContactForm, get_videos, get_playlist, get_read_video, bill, chek_bill, upload_google, send_to_mail, delete_videos

logging.basicConfig(level=logging.ERROR, filename="log.txt")


@app.route('/',  methods=['GET', 'POST'])
def index():
    form = ContactForm()
    return render_template("index.html", form=form)


@app.route('/video', methods=['POST'])
async def video():
    form_data = request.get_json()
    res = form_data["link"]
    try:
        res = form_data["link"]
        res = await get_videos(res)
        res["size"] = int(res["size"] * 0.14)
        chek = bill(res["size"])
        response = jsonify({"videos": res,
                            "pay_url": chek["bill"].pay_url,
                            "bill_id": chek["bill"].bill_id,
                            "comment": chek["comment"]})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except:
        return "0"


@app.route('/playlist', methods=['POST'])
async def playlist():
    form_data = request.get_json()
    res = form_data["link"]
    try:
        res = form_data["link"]
        res = await get_playlist(res)
        res["size"] = int(res["size"] * 0.14)
        chek = bill(res["size"])
        response = jsonify({"videos": res,
                            "pay_url": chek["bill"].pay_url,
                            "bill_id": chek["bill"].bill_id,
                            "comment": chek["comment"]})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except:
        return "0"


@app.route('/chek', methods=['POST', 'GET'])
async def chek():
    form_data = request.get_json()
    bill = form_data["bill_id"]
    try:
        chek = chek_bill(bill)
        if chek == "PAID":
            return "1"
        else:
            return "0"
    except:
        return "Incorrect response"


@app.route('/merge', methods=['POST', 'GET'])
async def merge():
    form_data = request.get_json()
    res = form_data["videos"]
    mail = form_data["email"]
    name = form_data["name"]
    try:
        video = await get_read_video(res, name)
        drive_link = upload_google(f'{name}.mp4', video)
        send_to_mail(drive_link, mail)
        await os.remove(video)
        response = jsonify(1)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except Exception as ex:
        return f"0\n{ex}"


@app.route('/delete', methods=['POST'])
async def delete():
    form_data = request.get_json()
    res = form_data["videos"]
    try:
        res = await delete_videos(res)
        return "1"
    except:
        return "0"
