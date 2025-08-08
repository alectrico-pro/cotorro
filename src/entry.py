#no reconoce el móudlo 
#from transbank.webpay.webpay_plus import WebpayPlus
#pip install transbank-sdk
import random
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

#const globals = pyodide.toPy({})
#globals.set('x', 123)
#globals.set('y', { a: 1, b: 2 } )

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



#importatnte, envia un formulario
#Text hay que incorporarlo WIP
async def enviar_formulario( request, env, text, fono):

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



async def on_fetch(request, env):
    url = urlparse(request.url)
    params = parse_qs(url.query)
    method = request.method

    console.log(f"Handling request {url.path} with params {params}")


    if url.path.startswith("/transbank") and method == 'GET':
        console.log(f"Params en /transbank {params}")
        buy_order = params['buy_order'][0]
        amount    = params['amount'][0]
        token, uri = await genera_link_de_pago_tbk( buy_order, amount, env.RETURN_URL, buy_order, env)
        pago_url= uri + "/?token_ws=" + token
        response = await post_tbk(pago_url, env)
        respuesta = response.redirect(pago_url, 307)
        return respuesta



    if url == "/return_url" and method == 'GET':
        console.log("En return_url")
        return Response.new('ok', status="200")


    if url.path.startswith("/webhook") and method == 'POST':
        console.log("En webhook")

        request_json = await request.json()
        console.log( f"request_json {request_json}")

        value = request_json.entry[0].changes[0].value

        console.log( f"value {value}")
        console.log( f"hasattr messages    {hasattr(value, 'messages')} " )
        console.log( f"hasattr contacts    {hasattr(value, 'contacts')} " )
        console.log( f"hasattr contacts    {hasattr(value, 'statuses')} " )


        if hasattr(value, 'messages') == True :
            console.log("Es un mensaje")

            #Cuando alguien escribe un texto en los canales de publico suscritos
            #Se recbie aquí
            #REspondeo con un cuestionario

            if hasattr(value.messages[0], 'text') == True :
               console.log("Es text")
               console.log(f"body {value.messages[0].text.body}")
               text = value.messages[0].text.body
               wa_id = request_json.entry[0].changes[0].value.contacts[0].wa_id
               await enviar_formulario( request, env, text, wa_id )
               return Response.new( text, status="200")
               
            #Cuando el usuario responde el cuestionario
            #Llega aquí
            #Lo proceso y le envío un resumen
            if hasattr(value.messages[0], 'interactive') == True :
               console.log("Es interactive")
               if hasattr(value.messages[0].interactive, 'nfm_reply') == True :
                   console.log("Es nfm_reply")
                   if hasattr(value.messages[0].interactive.nfm_reply, 'response_json') == True :
                       console.log("Tiene response_json")
                       await flow_reply_processor( request_json, env)
                       return Response.new('ok', status="200")

        elif hasattr(value, 'statuses') == True :
            console.log("Es un statuses")
            console.log(f"Status: {value.statuses[0].status}")
            if value.statuses[0].status == 'failed':
               console.log(f"Es failed, error: {value.statuses[0].errors[0].title}" )
            return Response.new('ok', status="200")
        else:
           console.log("No se ha identificado")
           return Response.new('ok', status="404")


#@app.route("/webhook", methods=["GET"])
#Hay que hacerlo nuevamente. Se me borró el que usé al comienzo
def webhook_get(request, env):
    console.log("En webhook_get")
    if params["hub.mode"] == ['subscribe'] and params['hub.verify_token'] == env.VERIFY_TOKEN:
        return Response(params['hub.challenge'][0], status=200)
    else:
        return Response("Error", status=403)


async def post_tbk( uri, env):
        options = {
               "method": "POST",
               "headers": {
                 "Tbk-Api-Key-Id":     f"{env.WEBPAY_API_KEY}",
                 "Tbk-Api-Key-Secret": f"{env.WEBPAY_SHARED_SECRET}" ,
                 "Content-Type":       "application/json",
               },
        }
        response = await fetch(uri, to_js(options))

        return reponse
        


#crea un link de pago tbk
async def genera_link_de_pago_tbk(buy_order, amount, return_url, session_id, env):

        uri     = f"{env.TBK_ENDPOINT}"

        body = {
          "buy_order":   buy_order,
          "amount":      amount,
          "return_url":  return_url,
          "session_id":  session_id,
        }

        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Tbk-Api-Key-Id":     f"{env.WEBPAY_API_KEY}",
                 "Tbk-Api-Key-Secret": f"{env.WEBPAY_SHARED_SECRET}" ,
                 "Content-Type":       "application/json",
               },
        }
        console.log(f"uri {uri}")
        console.log(f"body {body}")
        console.log(f"options {options}")
        console.log(f"uri {uri}")
        response = await fetch(uri, to_js(options))
        console.log(f"tbk response {response}")
        response_json = await response.json()
        token = response_json.token
        url   = response_json.url
        console.log(f"token {token}")
        console.log(f"url {url}")
        return token, url


#Se le envía un resumen de las respuestas del cuestionario
#Al que llenó el cuestionario
async def flow_reply_processor(request_json, env):
        console.log("En flow_reply_processor")
        #equest_json = await request.json()
        console.log( f"request_json {request_json}")
        value = request_json.entry[0].changes[0].value.contacts[0]
        console.log(f"value {value}")
        wa_id = request_json.entry[0].changes[0].value.contacts[0].wa_id
        console.log(f"wa_id: {wa_id}")
        response_json = request_json.entry[0].changes[0].value.messages[0].interactive.nfm_reply.response_json

        console.log(f"response_json {response_json}")


        #---- procesando los campos
        flow_data = json.loads(response_json)

        console.log(f"flow_data {flow_data}")
        sintoma_id = flow_data['sintomas']

        console.log(f"sintoma_id {sintoma_id}")

        sintoma_1=''
        sintoma_2=''
        sintoma_3=''
        sintoma_4=''
        sintoma_5=''
        sintoma_6=''

        match sintoma_id[0]:
            case "0":
                sintoma_1 = 'Sentí un ruido de cuetazo'
            case "1":
                sintoma_2 = 'Tengo enchufe(s) malo(s)'
            case "2":
                sintoma_3 = 'Necesito Instalar Luminarias'
            case "3":
                sintoma_4 = 'Necesito Presentar un TE1'
            case "4":
                sintoma_5 = 'Necesito más Circuitos'
            case "5":
                sintoma_6 = 'No tengo luz'

        nombre      = flow_data['nombre']
        apellido    = flow_data['apellido']
        fono        = flow_data['fono']
        email       = flow_data['email']
        direccion   = flow_data['direccion']
        descripcion = flow_data['descripcion']
        fecha       = flow_data['fecha']
        comuna      = flow_data['comuna']
        flow_token  = flow_data['flow_token']

        #un número único por exigencia de Transbank
        #uy_order  = str(uuid.uuid())

        buy_order  = str( random.randint(1, 10000))
        #amount debe ser calculado en base a lo ingresado en el cuestionario
        #por simplicidad se cobra solo la visita por ahora
        link_de_pago_tbk_url = env.GO_TBK_URL+"/?buy_order="+ buy_order +"&amount="+ str( env.AMOUNT)

        #ink_de_pago_tbk_url = await genera_link_de_pago_tbk( buy_order, env.AMOUNT, env.RETURN_URL, fono, env)

        reply = (
            f"Gracias por llenar el cuestionario. Estas son las respuestas que hemos guardado:\n\n"
            f"*Síntomas*\n\n"
            f"{sintoma_1}\n"
            f"{sintoma_2}\n"
            f"{sintoma_3}\n"
            f"{sintoma_4}\n"
            f"{sintoma_5}\n"
            f"{sintoma_6}\n\n"
            f"*Nombre:*\t{nombre}\n\n"
            f"*Apellido:*\t{apellido}\n\n"
            f"*Fono:*\t{fono}\n\n"
            f"*email:*\t{email}\n\n"
            f"*Dirección:*\t{direccion}\n\n"
            f"*Descripción:*\t{descripcion}\n\n"
            f"*Fecha:*\t{fecha}\n\n"
            f"*Comuna:*\t{comuna}\n\n"
            "------------------------------ \n\n"
            f"*Orden*:\t{buy_order}\n\n"
            "Por favor siga el link para pagar la visita en Transbank.\n"
            "Solo se paga la mano de obra.\n"
            "Ofrecemos crédito propio en seis cuotas mensuales sin interés con tarjeta de Crédito.\n"
            "Transbank captura el total pero UD. solo paga cuotas mensules.\n\n"
            f"*Link_de_pago:*\t{link_de_pago_tbk_url}\n\n"
            "------------------------------ \n\n"
        )

        console.log(f"reply {reply}")

        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"

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
                        "body" : reply }
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
        console.log(f"result{result}")

        return Response.new( reply, status="200")

