import flask
from flask import request
import requests
from playwright.sync_api import sync_playwright
import vertexai
from random import randint
from prompts import *
from flask_ngrok import run_with_ngrok
import json


config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 999999999999999
}


app = flask.Flask(__name__)
# run_with_ngrok(app, "2SLru5y12koqmYSaxstm7qH3sNJ_5ybBukkiny8iN2YMqSGAm")
cache = dict()

# url https://www.amazon.ca/Corsair-Vengeance-2x16GB-PC4-28800-Desktop/product-reviews/B08SPYCCF1/reviewerType=all_reviews

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}



@app.route("/")
def hello():
    res = flask.jsonify({"hello": "world"})

    return res


@app.route("/return_summary", methods=["GET", "POST"])
def process_url():
    id = request.args.get("id")  # Assuming the URL is sent as a form field
    if id is None:
        return "No id provided", 400
    
    if id in cache:
        res = flask.jsonify(cache[id])
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res

    # check if file json exists
    try:
        f = open(f"{id}.json", "r")
        res = flask.jsonify(json.loads(f.read()))
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res
    except:
        pass

    # Process the URL as needed
    # Example: Print the URL
    print("Received URL:", id)

    response = {
        "Product Name": "",
        "Image": "",
        "Rating": "",
        "Description": "",
        "Pros": "",
        "Cons": "",
        "Pricing": "",
        "Quality": "",
        "Performance": "",
        "Reliability": "",
    }
    data = {"Top": "", "Critical": ""}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()

        page = context.new_page()


        page.goto(f"https://www.amazon.ca/awgawg/dp/{id}/")
        response["Product Name"] = page.title()
        # get image from og:image
        page
        response["Image"] = page.locator('#landingImage').get_attribute(
            "src"
        )
        # document.getElementById("acrPopover").title
        response["Rating"] = page.query_selector("#acrPopover").get_attribute("title").replace(" out of 5 stars", "")
        response["Description"] = page.locator('#feature-bullets').inner_html().replace("About this item", "")

        page.goto(
            f"https://www.amazon.ca/lmao/product-reviews/{id}/reviewerType=all_reviews"
        )
        # Extract data using Playwright (replace with your own logic)
        response["Product Name"] = page.title().replace(
            "Amazon.ca:Customer reviews: ", ""
        )
        page.wait_for_timeout(1500)
        data["Top"] = page.inner_text(".reviews-content")
        page.goto(
            f"https://www.amazon.ca/lmao/product-reviews/{id}/reviewerType=all_reviews/ref=cm_cr_arp_d_viewopt_sr?filterByStar=critical"
        )
        page.wait_for_timeout(1500)
        data["Critical"] = page.inner_text(".reviews-content")
        browser.close()


    response["Pros"] = pros(data["Top"]).strip().replace(" •", "\n•")
    response["Cons"] = cons(data["Critical"]).strip().replace(" •", "\n•")
    response["Pricing"] = price(data["Top"]).strip().replace(" •", "\n•")
    response["Quality"] = quality(data["Top"]).strip().replace(" •", "\n•")
    response["Performance"] = performance(data["Top"]).strip().replace(" •", "\n•")
    response["Reliability"] = reliability(data["Top"]).strip().replace(" •", "\n•")

    cache[id] = response
    try:
        f = open(f"{id}.json", "w")
        f.write(json.dumps(response))
        f.close()
    except:1

    res = flask.jsonify(response)
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res

@app.route("/dummy", methods=["GET", "POST"])
def dummy():
    id = request.args.get("id")  # Assuming the URL is sent as a form field

    if id is None:
        return "No id provided", 400

    response = {
        "Product Name": id,
        "Image": "https://media.tenor.com/HnknA3u-W7kAAAAD/cat-meme.png",
        "Rating": 4.2,
        "Description": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s",
        "Pros": "abc_pros",
        "Cons": "abc_cons",
        "Pricing": "abc_pricing",
        "Quality": "abc_quality",
        "Performance": "abc_performance",
        "Reliability": "abc_reliability",
    }
    res = flask.jsonify(response)
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)