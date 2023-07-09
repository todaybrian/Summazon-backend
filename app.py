import flask
from flask import request
import requests
from playwright.sync_api import sync_playwright
import vertexai
from prompts import *

app = flask.Flask(__name__)

# url https://www.amazon.ca/Corsair-Vengeance-2x16GB-PC4-28800-Desktop/product-reviews/B08SPYCCF1/reviewerType=all_reviews

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/return_summary", methods=["GET", "POST"])
def process_url():
    id = request.args.get("id")  # Assuming the URL is sent as a form field
    if id is None:
        return "No id provided", 400
    # Process the URL as needed
    # Example: Print the URL
    print("Received URL:", id)

    response = {
        "Product Name": "",
        "Image": "",
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
        response["Image"] = page.locator('meta[property="og:image"]').get_attribute(
            "content"
        )

        page.goto(
            f"https://www.amazon.ca/lmao/product-reviews/{id}/reviewerType=all_reviews"
        )
        # Extract data using Playwright (replace with your own logic)
        response["Product Name"] = page.title().replace(
            "Amazon.ca:Customer reviews: ", ""
        )
        # extract description from metatag description
        response["Description"] = page.locator(
            'meta[name="description"]'
        ).get_attribute("content")
        data["Top"] = page.inner_text(".reviews-content")
        page.goto(
            f"https://www.amazon.ca/lmao/product-reviews/{id}/reviewerType=all_reviews/ref=cm_cr_arp_d_viewopt_sr?filterByStar=critical"
        )
        data["Critical"] = page.inner_text(".reviews-content")
        browser.close()

    response["Pros"] = pros(data["Top"])

    return flask.jsonify(data)


app.run(debug=True)
