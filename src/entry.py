import logging
from workers import fetch, handler
from pyodide.ffi import to_js as _to_js
#import requests no funciona en cloudflare workers
from workers import Response
from urllib.parse import urlparse, parse_qs
#import urllib3.request no existe
import urllib.request
import json
from js import console
import uuid
from js import Object, fetch, Response, Headers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#@handler
#async def on_scheduled(controller, env, ctx):


def to_js(obj):
    return _to_js(obj, dict_converter=Object.fromEntries)

# gather_response returns both content-type & response body as a string
async def gather_response(response):
    headers = response.headers
    content_type = headers["content-type"] or ""

    if "application/json" in content_type:
        return (content_type, json.dumps(dict(await response.json())))
    return (content_type, await response.text())


async def on_fetch(request, env):
    url = urlparse(request.url)
    params = parse_qs(url.query)
    method = request.method

    console.log(f"Handling request {url.path} with params {params}")


    #es solo para pruebas
    if url.path == "/envia_formulario":
        fono       = "56940338057"
        imagen_url = "https://www.alectrico.cl/assets/iconos/loguito.jpeg"
        uri        = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {env.META_USER_TOKEN}"
        }

        body = {
          "messaging_product": "whatsapp",
          "to": f"{fono}",
          "type": "template",
          "template": {
            "name": "say_visita",
            "language": {
              "code": "es"
          },
          "components": [
           { "type": "header", "parameters": [ { "type": "image",
                "image": {  "link": f"{imagen_url}" } } ] },
            { "type": "button", "sub_type": "flow",  "index": "0" }
           ]
          }
        }


        options = {
           "body": json.dumps(body),
           "method": "POST",
           "headers": {
             "Authorization": f"Bearer {env.META_USER_TOKEN}",
             "content-type": "application/json;charset=UTF-8"
           },
        }

        response = await fetch(uri, to_js(options))
        content_type, result = await gather_response(response)

        headers = Headers.new({"content-type": content_type}.items())
        return Response.new(result, headers=headers)


    # https://developers.cloudflare.com/workers/examples/post-json/
    # solo pruebas, envía un mensaje de pruebas
    if url.path == "/":
        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        #ri     = f"https://www.alectrico.cl/api/v1/santum/webhook"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {env.META_USER_TOKEN}"
        }
        body ={
             'messaging_product': 'whatsapp',
             'to': '56981370042',
             'type': 'template',
             'template': { 'name': 'prueba',
                           'language': {'code': 'en_US'}
             }
        }
        options = {
           "body": json.dumps(body),
           "method": "POST",
           "headers": {
             "Authorization": f"Bearer {env.META_USER_TOKEN}",
             "content-type": "application/json;charset=UTF-8"
           },
        }

        response = await fetch(uri, to_js(options))
        content_type, result = await gather_response(response)
 
        headers = Headers.new({"content-type": content_type}.items())
        return Response.new(result, headers=headers)

    #pruebas lee la respuesta del cuesionario
    #if url.path.startswith("/w") and method == 'POST':
    #    request_json = await request.json()
    #    response_json = request_json.entry[0].changes[0].value.messages[0].interactive.nfm_reply.response_json
    #    console.log(f"response_json {response_json}")
    #    return Response.new( response_json, status="200")

    #recibe todo tipo de mensajes
    #1. Mensajes envíados desde el celular cuando un cliente escribe algo en uno de los canales
    #2. Con cada body.text que llegue se enviará un cuestionario
    #3. Cada vez que un usuario reponda un cuestionario se le entegará un resumen y un botón
    #de pago.
    if url.path.startswith("/webhook") and method == 'POST':
        console.log("En webhook")
        flow_reply_procesor( request, env)
        """
        request_json = await request.json()
        value = request_json.entry[0].changes[0].value
        console.log("En try")
        wa_id = request_json.entry[0].changes[0].value.contacts[0].wa_id
        console.log("wa_id: {wa_id}")
        response_json = request_json.entry[0].changes[0].value.messages[0].interactive.nfm_reply.response_json

        console.log(f"response_json {response_json}")
        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        #ri     = f"https://www.alectrico.cl/api/v1/santum/webhook"

        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {env.META_USER_TOKEN}"
        }
        body = {
                    "messaging_product" :  "whatsapp",
                    "recipient_type"    :  "individual",
                    "to"                :  wa_id,
                    "type"              :  "text",
                    "text"              :  { "preview_url" : True,
                        "body" : response_json }
        }

        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {env.META_USER_TOKEN}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }

        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        return Response.new( response_json, status="200")
        try:
                mensaje = value.messages[0].text.body 
                console.log(f"mensaje {mensaje}")

                uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
                #ri     = f"https://www.alectrico.cl/api/v1/santum/webhook"

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {env.META_USER_TOKEN}"
                }
                body ={
                     'messaging_product': 'whatsapp',
                     'to': wa_id,
                     'type': 'template',
                     'template': { 'name': 'prueba',
                                   'language': {'code': 'en_US'}
                     }
                }
                options = {
                   "body": json.dumps(body),
                   "method": "POST",
                   "headers": {
                     "Authorization": f"Bearer {env.META_USER_TOKEN}",
                     "content-type": "application/json;charset=UTF-8"
                   },
                }

                response = await fetch(uri, to_js(options))
                console.log(f"response {response}")
                content_type, result = await gather_response(response)
                console.log(f"result {result}")
                console.log(f"content_type {content_type}")
                headers = Headers.new({"content-type": content_type}.items())


                #-- enviar el formulario a isa
                fono       = "56940338057"
                imagen_url = "https://www.alectrico.cl/assets/iconos/loguito.jpeg"
                uri        = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {env.META_USER_TOKEN}"
                }

                body = {
                  "messaging_product": "whatsapp",
                  "to": f"{fono}",
                  "type": "template",
                  "template": {
                    "name": "say_visita",
                    "language": {
                      "code": "es"
                  },
                  "components": [
                   { "type": "header", "parameters": [ { "type": "image",
                        "image": {  "link": f"{imagen_url}" } } ] },
                    { "type": "button", "sub_type": "flow",  "index": "0" }
                   ]
                  }
                }


                options = {
                   "body": json.dumps(body),
                   "method": "POST",
                   "headers": {
                     "Authorization": f"Bearer {env.META_USER_TOKEN}",
                     "content-type": "application/json;charset=UTF-8"
                   },
                }

                response = await fetch(uri, to_js(options))
                content_type, result = await gather_response(response)

                headers = Headers.new({"content-type": content_type}.items())
                return Response.new(result, headers=headers)

        except:
                return Response.new('ok', status="200")

       """

async def send(mensaje, env):
        console.log(f"En send {mensaje}")
        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        #ri     = f"https://www.alectrico.cl/api/v1/santum/webhook"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {env.META_USER_TOKEN}"
        }
        body ={
             'messaging_product': 'whatsapp',
             'to': '56981370042',
             'type': 'template',
             'template': { 'name': mensaje,
                           'language': {'code': 'en_US'}
             }
        }
        options = {
           "body": json.dumps(body),
           "method": "POST",
           "headers": {
             "Authorization": f"Bearer {env.META_USER_TOKEN}",
             "content-type": "application/json;charset=UTF-8"
           },
        }

        response = await fetch(uri, to_js(options))
        console.log(f"Desues de fetch {response}")
        content_type, result = await gather_response(response)

        headers = Headers.new({"content-type": content_type}.items())
        return Response.new(result, headers=headers)


#rutas -------------------------------------------------------------
#@app.route("/create-flow", methods=["POST"])
def create_flow():
    #field = (await request.json()).field
    #console.log( f"investigando body {field}" )

    flow_base_url = (
        f"https://graph.facebook.com/v18.0/{WHATSAPP_BUSINESS_ACCOUNT_ID}/flows"
    )
    flow_creation_payload = {"name": "<FLOW-NAME>", "categories": '["SURVEY"]'}
    flow_create_response = requests.request(
        "POST", flow_base_url, headers=auth_header, data=flow_creation_payload
    )

    try:
        global created_flow_id
        created_flow_id = flow_create_response.json()["id"]
        graph_assets_url = f"https://graph.facebook.com/v18.0/{created_flow_id}/assets"

        upload_flow_json(graph_assets_url)
        publish_flow(created_flow_id)

        print("FLOW CREATED!")
        return make_response("FLOW CREATED", 200)
    except:
        return make_response("ERROR", 500)


#@app.route("/webhook", methods=["GET"])
#no está adaptado, :no usa import request.no deja cloudflare
def webhook_get(request, env):
    console.log("En webhook_get")
    if params["hub.mode"] == ['subscribe'] and params['hub.verify_token'] == env.VERIFY_TOKEN:
        return Response(params['hub.challenge'][0], status=200)
    else:
        return Response("Error", status=403)

#@app.route("/webhook", methods=["POST"])
def webhook_post():
    # checking if there is a messages body in the payload
    console.log("En webhook_post")

    if (
        json.loads(request.body)["entry"][0]["changes"][0]["value"].get("messages")) is not None:
        """
        checking if there is a text body in the messages payload so that the sender's phone number can be extracted from the message
        """
        if (
            json.loads(request.body)["entry"][0]["changes"][0]["value"]["messages"][0].get("text")
        ) is not None:
            user_phone_number = json.loads(request.body)["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
            send_flow(created_flow_id, user_phone_number)
        else:
            flow_reply_processor(request)

    return Response("PROCESSED", status=200)



def flow_reply_procesor(request, env)
    flow_response = json.loads(request.get_data())["entry"][0]["changes"][0]["value"][
        "messages"
    ][0]["interactive"]["nfm_reply"]["response_json"]

    flow_data = json.loads(flow_response)
    uno:
        console.log("En webhook")
        request_json = await request.json()
        value = request_json.entry[0].changes[0].value
        console.log("En try")
        wa_id = request_json.entry[0].changes[0].value.contacts[0].wa_id
        console.log("wa_id: {wa_id}")
        response_json = request_json.entry[0].changes[0].value.messages[0].interactive.nfm_reply.response_json

        console.log(f"response_json {response_json}")
        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        #ri     = f"https://www.alectrico.cl/api/v1/santum/webhook"

        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {env.META_USER_TOKEN}"
        }
        body = {
                    "messaging_product" :  "whatsapp",
                    "recipient_type"    :  "individual",
                    "to"                :  wa_id,
                    "type"              :  "text",
                    "text"              :  { "preview_url" : True,
                        "body" : response_json }
        }

        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {env.META_USER_TOKEN}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }

        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        return Response.new( response_json, status="200")




def flow_reply_processor_original(request):
    flow_response = json.loads(request.get_data())["entry"][0]["changes"][0]["value"][
        "messages"
    ][0]["interactive"]["nfm_reply"]["response_json"]

    flow_data = json.loads(flow_response)
    source_id = flow_data["source"]
    tour_type_id = flow_data["tour_type"]
    tour_quality_id = flow_data["tour_quality"]
    decision_influencer_id = flow_data["decision_influencer"]
    tour_guides_id = flow_data["tour_guides"]
    aspects_enjoyed_id = flow_data["aspects_enjoyed"]
    improvements_id = flow_data["improvements"]
    recommend_id = flow_data["recommend"]
    return_booking_id = flow_data["return_booking"]

    match source_id:
        case "0":
            source = "Online search"
        case "1":
            source = "Social media"
        case "2":
            source = "Referral from a friend/family"
        case "3":
            source = "Advertisement"
        case "4":
            source = "Others"

    match tour_type_id:
        case "0":
            tour_type = "Cultural tour"
        case "1":
            tour_type = "Adventure tour"
        case "2":
            tour_type = "Historical tour"
        case "3":
            tour_type = "Wildlife tour"

    match tour_quality_id:
        case "0":
            tour_quality = "1 - Poor"
        case "1":
            tour_quality = "2 - Below Average"
        case "2":
            tour_quality = "3 - Average"
        case "3":
            tour_quality = "4 - Good"
        case "4":
            tour_quality = "5 - Excellent"

    match decision_influencer_id:
        case "0":
            decision_influencer = "Positive reviews"
        case "1":
            decision_influencer = "Pricing"
        case "2":
            decision_influencer = "Tour destinations offered"
        case "3":
            decision_influencer = "Reputation"

    match tour_guides_id:
        case "0":
            tour_guides = "Knowledgeable and friendly"
        case "1":
            tour_guides = "Knowledgeable but not friendly"
        case "2":
            tour_guides = "Friendly but not knowledgeable"
        case "3":
            tour_guides = "Neither of the two"
        case "4":
            tour_guides = "I didn’t interact with them"

    match aspects_enjoyed_id:
        case "0":
            aspects_enjoyed = "Tourist attractions visited"
        case "1":
            aspects_enjoyed = "Tour guide's commentary"
        case "2":
            aspects_enjoyed = "Group dynamics/interaction"
        case "3":
            aspects_enjoyed = "Activities offered"

    match improvements_id:
        case "0":
            improvements = "Tour itinerary"
        case "1":
            improvements = "Communication before the tour"
        case "2":
            improvements = "Transportation arrangements"
        case "3":
            improvements = "Advertisement"
        case "4":
            improvements = "Accommodation quality"

    match recommend_id:
        case "0":
            recommend = "Yes, definitely"
        case "1":
            recommend = "Yes, but with reservations"
        case "2":
            recommend = "No, I would not"

    match return_booking_id:
        case "0":
            return_booking = "Very likely"
        case "1":
            return_booking = "Likely"
        case "2":
            return_booking = "Undecided"
        case "3":
            return_booking = "Unlikely"



    reply = (
        f"Thanks for taking the survey! Your response has been recorded. This is what we received:\n\n"
        f"*How did you hear about our tour company?*\n{source}\n\n"
        f"*Which type of tour did you recently experience with us?*\n{tour_type}\n\n"
        f"*On a scale of 1 to 5, how would you rate the overall quality of the tour?*\n{tour_quality}\n\n"
        f"*What influenced your decision to choose our tour company?*\n{decision_influencer}\n\n"
        f"*How knowledgeable and friendly were our tour guides?*\n{tour_guides}\n\n"
        f"*What aspects of the tour did you find most enjoyable?*\n{aspects_enjoyed}\n\n"
        f"*Were there any aspects of the tour that could be improved?*\n{improvements}\n\n"
        f"*Would you recommend our tour company to a friend or family member?*\n{recommend}\n\n"
        f"*How likely are you to book another tour with us in the future?*\n{return_booking}"
    )

    user_phone_number = json.loads(request.get_data())["entry"][0]["changes"][0][
        "value"
    ]["contacts"][0]["wa_id"]
    send_message(reply, user_phone_number)


def send_message(message, phone_number, env):
    url     = f"https://graph.facebook.com/v18.0/{env.PHONE_NUMBER_ID}/messages"
    #    auth_header       = {"Authorization": f"Bearer {env.ACCESS_TOKEN}"}
    headers = {
     "Content-Type": "application/json",
     "Authorization": f"Bearer {env.META_USER_TOKEN}"
    }
    payload = json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": str(phone_number),
            "type": "text",
            "text": {"preview_url": False, "body": message},
        }
    )
    values = {
            "messaging_product": "whatsapp",
            "to": str(phone_number),
            "type": "text",
            "text": {"preview_url": False, "body": message},
    }
    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')
    req = urllib.request.Request(url, data=data, method="POST", headers = headers)
    console.log(f"req {req}")
    try:
         # Open the URL and send the request
         with urllib.request.urlopen(req) as response:
           # Read the response
           response_text = response.read().decode("utf-8")
           print(f"Status Code: {response.status}")
           print(f"Response: {response_text}")
    except urllib.error.URLError as e:
       print(f"Error: {e.reason}")
    except urllib.error.HTTPError as e:
       print(f"HTTP Error: {e.code} - {e.reason}")
  

  #requests.request("POST", messaging_url, headers=messaging_headers, data=payload)




def upload_flow_json(graph_assets_url):
    flow_asset_payload = {"name": "flow.json", "asset_type": "FLOW_JSON"}
    files = [("file", ("survey.json", open("survey.json", "rb"), "application/json"))]

    res = requests.request(
        "POST",
        graph_assets_url,
        headers=auth_header,
        data=flow_asset_payload,
        files=files,
    )
    print(res.json())


def publish_flow(flow_id):
    flow_publish_url = f"https://graph.facebook.com/v18.0/{flow_id}/publish"
    requests.request("POST", flow_publish_url, headers=auth_header)




def send_flow(flow_id, recipient_phone_number):
    # Generate a random UUID for the flow token
    flow_token = str(uuid.uuid4())

    flow_payload = json.dumps(
        {
            "type": "flow",
            "header": {"type": "text", "text": "Survey"},
            "body": {
                "text": "Your insights are invaluable to us – please take a moment to share your feedback in our survey."
            },
            "footer": {"text": "Click the button below to proceed"},
            "action": {
                "name": "flow",
                "parameters": {
                    "flow_message_version": "3",
                    "flow_token": flow_token,
                    "flow_id": flow_id,
                    "flow_cta": "Proceed",
                    "flow_action": "navigate",
                    "flow_action_payload": {"screen": "SURVEY_SCREEN"},
                },
            },
        }
    )

    payload = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": str(recipient_phone_number),
            "type": "interactive",
            "interactive": json.loads(flow_payload),
        }
    )

    requests.request("POST", messaging_url, headers=messaging_headers, data=payload)
    print("MESSAGE SENT")




