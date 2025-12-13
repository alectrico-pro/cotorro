
#Esto ahorra conexiones simulatneas
#Están limitdas a solo 6
#const response = await fetch(url);

#// Only read the response body for successful responses
#if (response.statusCode <= 299) {
#  // Call response.json(), response.text() or otherwise process the body
#} else {
#  // Explicitly cancel it
#  response.body.cancel();
#}

#no reconoce el móudlo 
#from transbank.webpay.webpay_plus import WebpayPlus
#pip install transbank-sdk

#Tratando de instalar con pip install
#pero cloudflare worker usa micropip
#import clipspy
import re
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
from js import Object, fetch, Headers

from datetime import date
from datetime import datetime
from datetime import timedelta

#from clips import Environment, Symbol


#const globals = pyodide.toPy({})
#globals.set('x', 123)
#globals.set('y', { a: 1, b: 2 } )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#@handler
#async def on_scheduled(controller, env, ctx):


#Probando workflows ------------------------------

from workers import WorkflowEntrypoint


#Esta siendo llamado desde fech/
class MyWorkflow(WorkflowEntrypoint):
    async def run(self, event, step):
        @step.do("my first step")
        async def my_first_step():
            # do some work
            return "Hello World!"

        await my_first_step()

#-----------------------------------------

def to_js(obj):
    return _to_js(obj, dict_converter=Object.fromEntries)

# gather_response returns both content-type & response body as a string
async def gather_response(response):
    headers = response.headers
    content_type = headers["content-type"] or ""
    if "application/json" in content_type:
        return (content_type, json.dumps(dict(await response.json())))
    return (content_type, await response.text())

#Envía un mensaje a usuarios fuera de la ventana
#Solo lo ocupao desde curl
async def send_aviso( env, fono, mensaje):
        console.log("En send_aviso")
        imagen_url = f"{env.API_URL}/{env.LOGUITO_PATH}"
        uri        = f"https://graph.facebook.com/v24.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {await env.META.get('IA_GALLEGO_USER_TOKEN')}"
        }
        body = {
          "messaging_product": "whatsapp",
          "to": f"{fono}",
          "type": "template",
          "template": {
            "name": "send_message",
            "language": {
              "code": "es"
          },
          "components": [
           { "type": "header", "parameters": [ { "type": "image",
                "image": {  "link": f"{imagen_url}" } } ] },
            { "type": "body",
              "parameters":
              [
                 {"type": "text", "parameter_name": "mensaje", "text": mensaje}                
              ] 
            }
           ]
          }
        }
        options = {
           "body": json.dumps(body),
           "method": "POST",
           "headers": {
             "Authorization": f"Bearer {await env.META.get('IA_GALLEGO_USER_TOKEN')}",
             "content-type": "application/json;charset=UTF-8"
           },
        }
        response = await fetch(uri, to_js(options))
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        result_dict = json.loads( result )
        id = result_dict['messages'][0]['id']
        console.log(f"id {id}")
        #---------------------------------------------------------------------------------------
        return Response( 'ok', status="200")





#no se usa por el momento, lo dejo por sí más
#adelante haya que enviar uno
#importatnte, envia un formulario
async def enviar_template_say_visita_flow_reserva( request, env, fono):
        console.log("En enviar_template say_visita -> flow reserva")
        imagen_url = f"{env.API_URL}/{env.LOGUITO_PATH}"
        uri        = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {await env.META.get('IA_GALLEGO_USER_TOKEN')}"
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
             "Authorization": f"Bearer {await env.META.get('IA_GALLEGO_USER_TOKEN')}",
             "content-type": "application/json;charset=UTF-8"
           },
        }
        #--- anota que se envió un cuestionario, porque podría darse como failed
        response = await fetch(uri, to_js(options))
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        result_dict = json.loads( result )
        id = result_dict['messages'][0]['id']
        console.log(f"id {id}")
        try:
          await env.FINANCIERO.put( id, 'say_visita -> flow reserva', { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION} )
        except:
          pass
        #---------------------------------------------------------------------------------------
        return Response( 'ok', status="200")

#----------------------------- WORKER ENTRYPOINT --------------------

async def on_fetch(request, env):

    url = urlparse(request.url)
    params = parse_qs(url.query)
    method = request.method
    console.log(f"Handling request {url.path} with params {params}")
    if url.path == "/favicon.ico":
          return Response("")


    #--------------------------------------------------------------------------------------------
    elif url.path == "/webhook_ai" and method == 'GET':
      if params["hub.mode"][0] == 'subscribe' and params['hub.verify_token'][0] == env.VERIFY_TOKEN:
        #bingo
        console.log("verificado ok")
        challenge = params["hub.challenge"][0]
        console.log(f"hub.challenge {challenge}")
        return Response( str(challenge), status=200)
      else:
        return Response("Error", status=403)

    #----------------- WEBHOOK DE WABA ---------------------------------------------------------
    elif url.path.startswith("/webhook_ai") and method == 'POST':  
        console.log("En webhook_ai")
        request_json = await request.json()
        value        = request_json.entry[0].changes[0].value
        if hasattr(value, 'messages') == True :
            if hasattr(value.messages[0], 'text') == True :
               console.log("Es text")
               console.log(f"body {value.messages[0].text.body}")
               descripcion = value.messages[0].text.body
               id          = value.messages[0].id
               wa_id       = request_json.entry[0].changes[0].value.contacts[0].wa_id
               respuesta = await infonas( env, wa_id, descripcion)
               #Solo lo ocupo desde curl
               #await send_aviso( env, wa_id, respuesta )
               return Response( "Procesado", status="200")
            else:
              console.log(f"Es un mensaje y nada más: {value.messages[0]}")
              return Response( "no procesado", status="200")
        else:
          console.log(f"No es un mensaje")
          return Response( "no procesado", status="200")
    else:
        console.log("No se ha identificado")
        return Response( "no se ha identificado", status="200")
#----------------------------FIN llegada de requests --------------------------


#----------------------------- FUNCIONES ------------------------------------------------------

#Transformarlo para usarlo más adelante
def to_markdown( voucher):
      TXT = f"""
      -----
      Comprobante de Pago Electrónico (Voucher)

      Estos son los datos del pago, que Ud. ha realizado en Transbank. El valor inluye IVA y estará registrado en la Contabilidad de alectrico® spa. \n
      \n *card_number* {voucher.card_detail.card_number} \n *buy_order* {voucher.buy_order} \n *session_id* {voucher.session_id} \n *amount* {voucher.amount} \n *transaction_date* {voucher.transaction_date} \n *accounting_date* {voucher.accounting_date} \n *authorization_code* {voucher.authorization_code} \n *response_code* {voucher.response_code} \n *installments_number* {voucher.installments_number} \n *status* {voucher.status} \n *payment_type_code* {voucher.payment_type_code} \n\n
      ----
      """
      return TXT

#Lo estoy usando
async def send_message( env, wa_id, msg):
        console.log( "En send_message")
        console.log(f"wa_id {wa_id}")
        console.log( f"msg  {msg}")

        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {await env.META.get('IA_GALLEGO_USER_TOKEN')}"
        }
        body = {
                    "messaging_product" :  "whatsapp",
                    "recipient_type"    :  "individual",
                    "to"                :  wa_id,
                    "type"              :  "text",
                    "text"              :  { "preview_url" : True, "body"        : msg }
        }
        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {await env.META.get('IA_GALLEGO_USER_TOKEN')}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return Response( msg, status="200")


#Todavía no lo uso, pero es probable que lo use
async def send_reply( env, wa_id, reply):

        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {await env.META.get('IA_GALLEGO_USER_TOKEN')}"
        }
        body = {
                    "messaging_product" :  "whatsapp",
                    "recipient_type"    :  "individual",
                    "to"                :  wa_id,
                    "type"              :  "text",
                    "text"              :  { "preview_url" : True,  "body" : reply }
        }
        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {await env.META.get('IA_GALLEGO_USER_TOKEN')}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result{result}")
        return Response( reply, status="200")



#---- Información de narcos as a service
#WIP
async def infonas( env, wa_id, prompt ):
      console.log("Estoy en infonas")

      # answer = await env.AI.autorag("square-cloud-8e93").aiSearch( to_js(
      # {
      # "query": prompt, "model": "@cf/meta/llama-3.3-70b-instruct-fp8-fast", "rewrite_query": True, "max_num_results": 2, "ranking_options": { "score_threshold": 0.3  }}))

      #context window: 32000
      #@cf/meta/llama-3.1-8b-instruct-fp8
      modelo = await env.MODELO.get('NX_MODELO_RAG') 
      try:
        answer = await env.AI.autorag("solitary-night-02b5").aiSearch( to_js(
        { "query": prompt, "model": modelo, "rewrite_query": True,
          "max_num_results": 12, "ranking_options": { "score_threshold": 0.3  }}))
        respuesta = answer.response
      except Exception as e:
        respuesta = f"Bah! Se nos agotaron las neuronas, reintente mañana. {e}  :)"

      console.log(f"{respuesta}")
      reply = (
      "NX 9020000 2018-2025 \n"
      ".............................\n"
      f"{respuesta} \n"
      "..................... \n "
     "alectrico®\n "
      )
      await send_reply( env, wa_id, reply)
      await send_aviso( env, wa_id, respuesta)
      return respuesta



