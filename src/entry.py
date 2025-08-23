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
from clips import Environment, Symbol


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
async def enviar_template_say_visita_flow_reserva( request, env, fono):
        console.log("En enviar_template say_visita -> flow reserva")
        imagen_url = f"{env.API_URL}/{env.LOGUITO_PATH}"
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
        return Response(result, headers=headers)


async def on_fetch(request, env):

    url = urlparse(request.url)
    params = parse_qs(url.query)
    method = request.method

    console.log(f"Handling request {url.path} with params {params}")

    if url.path == '/create_from_landing_page' and method== 'POST':
        console.log(f"Params en /create_from_landing_page {params}")

        body = await request.text()
        buy_order    = str( random.randint(1, 10000))

        session_id   = buy_order
        amount       = env.AMOUNT
        params       = parse_qs( body )

        name         = params['data[0][]'][1]
        fono         = params['data[1][]'][1]
        email        = params['data[2][]'][1]
        direccion    = params['data[3][]'][1]
        comuna       = params['data[4][]'][1]
        descripcion  = params['data[5][]'][1]
        #landing_page = params['data[6][]'][1]

        token_ws, uri = await genera_link_de_pago_tbk( buy_order, amount, env.RETURN_URL, session_id, env)
        await say_tomar(env, str(env.FONO_JEFE), name, direccion, comuna )
        path_de_pago = f"/transbank?amount={env.AMOUNT}&session_id={fono}&buy_order={buy_order}"
        await say_link_de_pago( env, fono, name, descripcion, comuna, path_de_pago )
        headers =  { "Access-Control-Allow-Origin": "*" }
        return Response( 'ok', status="200", headers=headers )



    elif url.path == "/favicon.ico":
          return Response("")


    #Esto viende del QR de la chaqueta
    #https://www.alectrico.cl/v/uR21SF_P0pnd8rQAMGSfEg/verifica_user
    elif url.path == '/v/uR21SF_P0pnd8rQAMGSfEg/verifica_user':
        await say_jefe(env, f"Hola Jefe, alguien llegó a verifica_user" )
        return Response.redirect( env.ALEC_SEC_URL, 307)
        #return agendar(env, '/v/uR21SF_P0pnd8rQAMGSfEg/verifica_user')


    elif url.path == '/':
        return agendar(env, 'Ingrese los datos para Agendar una Visita a Domicilio')



       #agendar?nombre=oipoi+upoi&fono=987654321&email=hjhkjh%40lkjlkj.ll&comuna=Providencia&descripcion=lkñ+jñlkj&direccion=o+ṕoiṕoiṕo&latitude=&longitude=&amount=68000
    elif url.path == '/agendar':
        console.log(f"Params en /agendar {params}")
        buy_order   = str( random.randint(1, 10000))
        session_id  = buy_order
        amount      = params['amount'][0]
        fono        = params['fono'][0]
        descripcion = params['descripcion'][0]
        amount      = params['amount'][0]

        await enviar_template_say_visita_flow_reserva(request, env, fono )
        await say_jefe( env, f"en agendar {fono} {descripcion}")


        reply   = (
                    f"*buy_order*    { buy_order}     \n"
                    f"*amount*       { amount}        \n"
                    f"*fono*         { fono     }    \n"
                    f"*descripcion*  { descripcion } \n"
                  )

        token_ws, uri = await genera_link_de_pago_tbk( buy_order, amount, env.RETURN_URL, session_id, env)
        await say_jefe(env, reply )
        return mostrar_formulario_de_pago(request, env, buy_order, amount, uri, token_ws)


    elif url.path.startswith("/transbank") and method == 'GET':
        console.log(f"Params en /transbank {params}")
        buy_order  = params['buy_order'][0]
        amount     = params['amount'][0]
        session_id = params['session_id'][0]

        token_ws, uri = await genera_link_de_pago_tbk( buy_order, amount, env.RETURN_URL, session_id, env)
        return mostrar_formulario_de_pago(request, env, buy_order, amount, uri, token_ws)


    elif url.path == "/return_url" and 'token_ws' in params:
        token_ws = params['token_ws'][0]
        console.log(f"En return_url token_ws: {token_ws}")
        await tbk_commit( token_ws, env)
        return mostrar_success(env, " Envíamos el Comprobante del Pago, a Su Whatsapp ")


    elif url.path == "/return_url" and 'TBK_TOKEN' in params:
        console.log("En return_url TKB_TOKEN {TKB_TOKEN}")
        return mostrar_not_found(env, "El Pago fue Cancelado! ")


    elif url.path.startswith("/webhook") or url.path.startswith("/api/v1/santum/webhook"):
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
            #Se recibe aquí
            #REspondo con un cuestionario

            if hasattr(value.messages[0], 'text') == True :
               console.log("Es text")
               console.log(f"body {value.messages[0].text.body}")
               body = value.messages[0].text.body
               wa_id = request_json.entry[0].changes[0].value.contacts[0].wa_id
               await enviar_template_say_visita_flow_reserva( request, env, wa_id )
               await say_jefe(env, f"Hola Jefe, alguien escribió: {body}----{wa_id}" )
               return Response( "Procesado", status="200")

               
            #Cuando el usuario responde el cuestionario
            #Llega aquí
            #Lo proceso y le envío un resumen
            if hasattr(value.messages[0], 'interactive') == True :
               console.log("Es interactive")
               if hasattr(value.messages[0].interactive, 'nfm_reply') == True :
                   console.log("Es nfm_reply")
                   if hasattr(value.messages[0].interactive.nfm_reply, 'response_json') == True :
                       console.log("Tiene response_json")
                       return await flow_reply_processor( request_json, env)

            console.log(f"Es un mensaje y nada más: {value}")
            return Response( "no procesado", status="200")



        elif hasattr(value, 'statuses') == True :
            console.log("Es un statuses")
            status = value.statuses[0].status
            console.log(status)
            if  status == 'failed' and value.statuses[0].errors[0].title == 'Message undeliverable':
               console.log(f"Es failed, error: {value.statuses[0].errors[0].title}" )
               wa_id        = request_json.entry[0].changes[0].value.statuses[0].recipient_id
               buy_order    = str( random.randint(1, 10000))
               link_de_pago = f"{env.API_URL}/transbank?amount={env.AMOUNT}&session_id={wa_id}&buy_order={buy_order}"
               #esto genera utro Message undeliverable
               msg        = (f"Por favor pague la visita siguiendo el link:\n"
                            f"link_de_pago: {link_de_pago}\n\n")
               return await send_msg(env, wa_id, msg)
            return Response( "ok", status="200")



    elif url.path.startswith('/fonos.json'):
        console.log("En fonos.json")
        return fonos(env)

    else:     
      console.log("No se ha identificado")
      return mostrar_not_found(env, "Bah! Ocurrió un Error")

#.......................... MENU PRINCIPAL -----------------------------------

#@app.route("/webhook", methods=["GET"])
#Hay que hacerlo nuevamente. Se me borró el que usé al comienzo
def webhook_get(request, env):
    console.log("En webhook_get")
    if params["hub.mode"] == ['subscribe'] and params['hub.verify_token'] == env.VERIFY_TOKEN:
        return Response(params['hub.challenge'][0], status=200)
    else:
        return Response("Error", status=403)


async def post_tbk( uri, env):
    init = {
        "method": "POST",
        "headers": {
            "Content-Type": "application/json;charset=UTF-8",
            "Tbk-Api-Key-Id":     f"{env.WEBPAY_API_KEY}",
            "Tbk-Api-Key-Secret": f"{env.WEBPAY_SHARED_SECRET}" ,
        }
    }
    response = await fetch(uri, init)
    return response
        

async def tbk_commit( token_ws, env):
   console.log("En tbk_commit")
   uri = f"{env.TBK_ENDPOINT}/{token_ws}"
   options = {
        "method": "PUT",
        "headers": {
            "Content-Type": "application/json;charset=UTF-8",
            "Tbk-Api-Key-Id":     f"{env.WEBPAY_API_KEY}",
            "Tbk-Api-Key-Secret": f"{env.WEBPAY_SHARED_SECRET}" ,
        }
   }
   console.log(f"uri {uri}")
   response      = await fetch(uri, to_js(options))
   console.log(f"response {response}")
   response_json = await response.json()
   console.log(f"response_json {response_json}")
   await send_voucher( response_json, response_json.session_id, env)
   return await say_jefe(env, f"Pagado {response_json.buy_order}----{response_json.session_id}" )
   #respondo ok sin esperar al resultado de send_voucher
   return Response('ok', status="200")
   

#installments_amount no está en la tarjeta de prueba AmericanExpress
#vci no está en la tarjeta Mach
#balance tampoco
def to_markdown( voucher):
      TXT = f"""
      -----
      Comprobante de Pago Electrónico (Voucher)

      Estos son los datos del pago, que Ud. ha realizado en Transbank. El valor inluye IVA y estará registrado en la Contabilidad de alectrico® spa. \n
      \n *card_number* {voucher.card_detail.card_number} \n *buy_order* {voucher.buy_order} \n *session_id* {voucher.session_id} \n *amount* {voucher.amount} \n *transaction_date* {voucher.transaction_date} \n *accounting_date* {voucher.accounting_date} \n *authorization_code* {voucher.authorization_code} \n *response_code* {voucher.response_code} \n *installments_number* {voucher.installments_number} \n *status* {voucher.status} \n *payment_type_code* {voucher.payment_type_code} \n\n
      ----
      """
      return TXT


async def send_voucher( voucher_json, wa_id, env):
   console.log(f"voucher_json {voucher_json}")
   reply = to_markdown( voucher_json )
   console.log(f"reply {reply}")
   return await send_reply(env, wa_id, reply)


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
        link_de_pago_tbk_url = env.GO_TBK_URL+"/?buy_order="+ buy_order +"&amount="+ str( env.AMOUNT) + "&session_id=" + str(wa_id)

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
        await send_reply(env, wa_id, reply)
        console.log("Enviando reply al FONO_JEFE")
        return await send_msg(env, str(env.FONO_JEFE), reply )


async def say_jefe(env, descripcion):
        return await say_tomar( env, str(env.FONO_JEFE), 'ALEC', descripcion, 'PROVIDENCIA')


async def say_tomar( env, wa_id, nombre, descripcion, comuna ):
        console.log("En say_tomar")
        console.log(f"wa_id {wa_id}")
        console.log( f"descripcion  {descripcion}")

        body = { "messaging_product" :  "whatsapp",
                "to"                   :  wa_id,
                "type"                 :  "template",
                "template"             : { "name" : "say_tomar", "language" : { "code" : "es" },
                    "components"           : [  { "type" :   "body",
                        "parameters" : [
              { "type"             :   "text", "text" : nombre    } ,
              { "type"             :   "text", "text" : descripcion } ,
              { "type"             :   "text", "text" : comuna    }
            ] } ] }}

        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {env.META_USER_TOKEN}"
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
        return



async def say_link_de_pago( env, wa_id, nombre, descripcion, comuna, path_de_pago ):
        console.log("En say_link_de_pago")
        console.log(f"wa_id {wa_id}")
        console.log( f"descripcion  {descripcion}")
        console.log( f"link_de_pago  {path_de_pago}")

        imagen_url = f"{env.API_URL}/{env.LOGUITO_PATH}"

        body = {"messaging_product"    :  "whatsapp",
                "to"                   :  wa_id,
                "type"                 : "template",
                "template"             : { "name" : "saludo",
                                       "language" : { "code" : "es_AR" },
                "components"           : [
                { "type": "header",  "parameters": [
                   { "type" : "image",
                     "image": { "link": imagen_url } } ] },
                { "type" :   "body", "parameters" : [
                   { "type"            :   "text", "text" : nombre    } ,
                   { "type"            :   "text", "text" : descripcion } ] },
                { "type"    : "button",
                     "sub_type": "url", 
                     "index"   : "0",
                   "parameters": [ { "type": "text", "text": path_de_pago}]}]}}


        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {env.META_USER_TOKEN}"
        }
        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {env.META_USER_TOKEN}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        console.log(f"body {body}")
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return



async def send_msg( env, wa_id, msg):
        console.log( "En send_msg")
        console.log(f"wa_id {wa_id}")
        console.log( f"msg  {msg}")

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
                                             "body"        : msg }
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
        return Response( msg, status="200")


#sujeto a reenganche
async def send_reply( env, wa_id, reply):

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
        return Response( reply, status="200")


#Funciona para android > 5
def mostrar_formulario_de_pago(request, env, buy_order, amount, pago_url, token_ws):
  avisar = True
  CSS = "body { color: red; }"
  HTML = f"""<!DOCTYPE html>
<html lang='es-CL' prefix='og: http://ogp.me/ns#'  >
<head>
  <meta charset='UTF-8'>
  <meta http-equiv='X-UA-Compatible' content='IE=edge'>
  <meta name='generator' content='Mobirise v5.1.8, mobirise.com'>
  <meta name='twitter:card' content='summary_large_image'/>
  <meta name='twitter:image:src' content={env.LOGUITO_PATH}>
  <meta property='og:image' content={env.LOGUITO_PATH}>
  <meta name='twitter:title' content='Eléctrico a Domicilio Providencia'>
  <meta name='viewport' content='width=device-width, initial-scale=1, minimum-scale=1'>
  <link rel='shortcut icon' href='https://alectrico.cl/assets/images/locoalicate-96x155.png' type='image/x-icon'>
  <meta name='description' content='Eléctrico a Domicilio Providencia'>


  <title>Eléctrico a Domicilio Providencia</title>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/web/assets/mobirise-icons2/mobirise2.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/web/assets/mobirise-icons/mobirise-icons.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/tether/tether.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap-grid.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap-reboot.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/dropdown/css/style.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/animatecss/animate.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/socicon/css/styles.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/theme/css/style.css'>
  <link rel='preload' as='style' href='{env.ASSETS_SERVER_URL}/mobirise/css/mbr-additional.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/mobirise/css/mbr-additional.css' type='text/css'>

</head>

<body>

  <section class='menu menu2 cid-sewGNRqCZx' once='menu' id='menu2-2'>
    <nav class='navbar navbar-dropdown navbar-fixed-top navbar-expand-lg'>
      <div class='container'>
        <div class='navbar-brand'>
          <span class='navbar-logo'>
            <a href='https://{env.TLD}.cl'>
              <img src='{env.ASSETS_SERVER_URL}/images/locoalicate-96x155.png' alt='a' style='height: 3rem;'>
            </a>
          </span>
          <span class='navbar-caption-wrap'><a class='navbar-caption text-white text-primary display-4' href='#top'>ALECTRICO</a></span>
        </div>
      </div>
    </nav>
  </section>

  <section class='header1 cid-sewsPSgeos mbr-parallax-background' id='header1-1'>
    <div class='container-fluid'>
        <div class='row justify-content-center'>
            <div class='col-12 col-lg-11'>
              <h1 class='mbr-section-title mbr-fonts-style mb-3 display-4'><strong><em>Eléctricos a Domicilio </em></strong><br><strong><em>- en Providencia -</em></strong></h1>
              <h2 class='mbr-section-subtitle mbr-fonts-style mb-3 display-5'>{env.MISION}</h2>
              <div class='mbr-section-btn mt-3'><a class='btn btn-primary display-4' href='https://wa.me/56945644889'>
              <span class='socicon socicon-whatsapp mbr-iconfont mbr-iconfont-btn'>
              </span></a> <a class='btn btn-info display-4' href='tel:+56932000849'><span class='mobi-mbri mobi-mbri-phone mbr-iconfont mbr-iconfont-btn'></span></a></div>
            </div>
        </div>
    </div>
  </section>
  <section class='mbr-section form4 cid-qAUteatZnl' id='form4-8e' style='border-top-style: solid;border-top-width: 0px;right: -;margin-bottom: 100px;margin-top: 50px;' >
    <div class='container'>
      <h1 class='mbr-section-title mbr-fonts-style mb-3 display-4'><strong><em>Servicio de Electricista a Domicilio </em></strong><br><strong><em>- en Providencia -</em></strong></h1>
      <h2 class='mbr-section-subtitle mbr-fonts-style mb-3 display-5'>Este servicio tienen un costo con IVA de:</h2>
      <div class='row'>
        <div class='offset-md-3 col-md-6'>
          <div>
              </span>
              <div class='col-7 col-md-6' multi-horizontal data-for='amount'>
                <input type='text' readonly='' value = {amount} class='form-control input' id='amount' name='amount' data-form-field='Text' placeholder='Monto a Pagar' required=''>
              </div>
        </div>
       <div data-form-type='formoid'>
          <form class='block mbr-form' action={pago_url} method='post' data-form-title='Agendar Form'>
              <div class='col-md-4' data-for='token_ws'>
                <input type='text' readonly='' hidden='' value = {token_ws} class='form-control input' id='token_ws' name='token_ws' data-form-field='token_ws' placeholder='token_ws' required=''>
              </div>
              <div class='input-group-btn col-md-12' style='margin-top: 10px;'><button href='' type='submit' class='btn btn-primary btn-form display-4'>Pagar</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</section>


<section class='barter1 cid-sezOMgUKyB' once='barters' data-bg-video={env.VIDEO_URL} id='barter1-f'>
  <div class='mbr-overlay' style='opacity: 0.6; background-color: rgb(35, 35, 35);'></div>
    <div class='container'>
      <div class='row mbr-white'>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Solo para Ud.</strong></h5>
          <ul class='list mbr-fonts-style display-4'>
            <li class='mbr-text item-wrap'><a href='https://designer.alectrico.cl' class='text-primary'>Designer</a></li>
            <li class='mbr-text item-wrap'><a href='https://registro.alectrica.cl' class='text-primary'>Registro</a></li><li class='mbr-text item-wrap'><a href='https://tips.alectrico.cl' class='text-primary'>Tips</a></li>
          </ul>
        </div>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Reclamos</strong></h5>
            <ul class='list mbr-fonts-style display-4'>
              <li class='mbr-text item-wrap'><a href='https://tico.alectrico.cl' class='text-primary'>tico.alectrico.cl</a></li>
            </ul>
        </div>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Qué es esto?</strong></h5>
          <p class='mbr-text mbr-fonts-style mb-4 display-4'>ALECTRICO<br>Es un lugar de encuentro entre personas con problemas eléctricos y los profesionales que sean capaces de resolverlos.</p>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-3 display-5'>Botones de Pánico<strong></strong></h5>
          <div class='social-row display-7'>

           <div class='soc-item'>
              <a href='https://repair.{env.TLD}.cl' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-cash mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://www.{env.TLD}.cl/agendar' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-edit-2 mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://www.{env.TLD}.cl/agendar'>
                <span class='mbr-iconfont mobi-mbri-setting mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://registro.alectrica,cl' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-user mobi-mbri'></span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
</section>

<script>
  function getLocation() {{ if (navigator.geolocation) {{ navigator.geolocation.getCurrentPosition(showPosition); }} else {{}} }}
  function showPosition(position) {{
    document.getElementById('latitude').value  = position.coords.latitude.toString(10);
    document.getElementById('longitude').value = position.coords.longitude.toString(10); }}
</script>

  <script src='{env.ASSETS_SERVER_URL}/web/assets/jquery/jquery.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/popper/popper.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/tether/tether.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/bootstrap/js/bootstrap.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/smoothscroll/smooth-scroll.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/dropdown/js/nav-dropdown.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/dropdown/js/navbar-dropdown.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/touchswipe/jquery.touch-swipe.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/viewportchecker/jquery.viewportchecker.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/parallax/jarallax.min.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/ytplayer/jquery.mb.ytplayer.min.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/vimeoplayer/jquery.mb.vimeo_player.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/theme/js/script.js'></script>
  <div id='scrollToTop' class='scrollToTop mbr-arrow-up'><a style='text-align: center;'>
    <i class='mbr-arrow-up-icon mbr-arrow-up-icon-cm cm-icon cm-icon-smallarrow-up'></i></a>
  </div>
  <input name='animation' type='hidden'>
</body>
</html>
"""
  headers = {"content-type": "text/html"}
  return Response(HTML, headers=headers)



def mostrar_not_found( env, mensaje):

  HTML = f"""<!DOCTYPE html>
<html lang='es-CL' prefix='og: http://ogp.me/ns#'  >
<head>
  <meta charset='UTF-8'>
  <meta http-equiv='X-UA-Compatible' content='IE=edge'>
  <meta name='generator' content='Mobirise v5.1.8, mobirise.com'>
  <meta name='twitter:card' content='summary_large_image'/>
  <meta name='twitter:image:src' content={env.LOGUITO_PATH}>
  <meta property='og:image' content={env.LOGUITO_PATH}>
  <meta name='twitter:title' content='Eléctrico a Domicilio Providencia'>
  <meta name='viewport' content='width=device-width, initial-scale=1, minimum-scale=1'>
  <link rel='shortcut icon' href='https://alectrico.cl/assets/images/locoalicate-96x155.png' type='image/x-icon'>
  <meta name='description' content='Eléctrico a Domicilio Providencia'>


  <title>Eléctrico a Domicilio Providencia</title>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/web/assets/mobirise-icons2/mobirise2.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/web/assets/mobirise-icons/mobirise-icons.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/tether/tether.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap-grid.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap-reboot.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/dropdown/css/style.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/animatecss/animate.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/socicon/css/styles.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/theme/css/style.css'>
  <link rel='preload' as='style' href='{env.ASSETS_SERVER_URL}/mobirise/css/mbr-additional.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/mobirise/css/mbr-additional.css' type='text/css'>

</head>

<body>

  <section class='menu menu2 cid-sewGNRqCZx' once='menu' id='menu2-2'>
    <nav class='navbar navbar-dropdown navbar-fixed-top navbar-expand-lg'>
      <div class='container'>
        <div class='navbar-brand'>
          <span class='navbar-logo'>
            <a href='https://{env.TLD}.cl'>
              <img src='{env.ASSETS_SERVER_URL}/images/locoalicate-96x155.png' alt='a' style='height: 3rem;'>
            </a>
          </span>
          <span class='navbar-caption-wrap'><a class='navbar-caption text-white text-primary display-4' href='#top'>ALECTRICO</a></span>
        </div>
      </div>
    </nav>
  </section>

  <section class='header1 cid-sewsPSgeos mbr-parallax-background' id='header1-1'>
    <div class='container-fluid'>
        <div class='row justify-content-center'>
            <div class='col-12 col-lg-11'>
              <h1 class='mbr-section-title mbr-fonts-style mb-3 display-4'><strong><em>Eléctricos a Domicilio </em></strong><br><strong><em>- en Providencia -</em></strong></h1>
              <h2 class='mbr-section-subtitle mbr-fonts-style mb-3 display-5'>{env.MISION}</h2>
              <div class='mbr-section-btn mt-3'><a class='btn btn-primary display-4' href='https://wa.me/56945644889'>
              <span class='socicon socicon-whatsapp mbr-iconfont mbr-iconfont-btn'>
              </span></a> <a class='btn btn-info display-4' href='tel:+56932000849'><span class='mobi-mbri mobi-mbri-phone mbr-iconfont mbr-iconfont-btn'></span></a></div>
            </div>
        </div>
    </div>
  </section>

  <section class='mbr-section form4 cid-qAUteatZnl' id='form4-8e' style='border-top-style: solid;border-top-width: 0px;right: -;margin-bottom: 100px;margin-top: 50px;' >
    <div class='container'>
      <h1 class='mbr-section-title mbr-fonts-style mb-3 display-4'><strong><em>{mensaje} </em></strong><br><strong><em>- Uhm! a veces hay que intentarlo de nuevo :) -</em></strong></h1>
      <div class='row'>
        <div class='offset-3'>
           <img src="icon/fail.png" width="150" height="150" alt="fail">
        </div>
      </div>
    </div>
  </section>

<section class='barter1 cid-sezOMgUKyB' once='barters' data-bg-video={env.VIDEO_URL} id='barter1-f'>
  <div class='mbr-overlay' style='opacity: 0.6; background-color: rgb(35, 35, 35);'></div>
    <div class='container'>
      <div class='row mbr-white'>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Solo para Ud.</strong></h5>
          <ul class='list mbr-fonts-style display-4'>
            <li class='mbr-text item-wrap'><a href='https://designer.alectrico.cl' class='text-primary'>Designer</a></li>
            <li class='mbr-text item-wrap'><a href='https://registro.alectrica.cl' class='text-primary'>Registro</a></li><li class='mbr-text item-wrap'><a href='https://tips.alectrico.cl' class='text-primary'>Tips</a></li>
          </ul>
        </div>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Reclamos</strong></h5>
            <ul class='list mbr-fonts-style display-4'>
              <li class='mbr-text item-wrap'><a href='https://tico.alectrico.cl' class='text-primary'>tico.alectrico.cl</a></li>
            </ul>
        </div>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Qué es esto?</strong></h5>
          <p class='mbr-text mbr-fonts-style mb-4 display-4'>ALECTRICO<br>Es un lugar de encuentro entre personas con problemas eléctricos y los profesionales que sean capaces de resolverlos.</p>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-3 display-5'>Botones de Pánico<strong></strong></h5>
          <div class='social-row display-7'>

           <div class='soc-item'>
              <a href='https://repair.{env.TLD}.cl' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-cash mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://www.{env.TLD}.cl/agendar' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-edit-2 mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://www.{env.TLD}.cl/agendar'>
                <span class='mbr-iconfont mobi-mbri-setting mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://registro.alectrica,cl' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-user mobi-mbri'></span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
</section>

<script>
  function getLocation() {{ if (navigator.geolocation) {{ navigator.geolocation.getCurrentPosition(showPosition); }} else {{}} }}
  function showPosition(position) {{
    document.getElementById('latitude').value  = position.coords.latitude.toString(10);
    document.getElementById('longitude').value = position.coords.longitude.toString(10); }}
</script>

  <script src='{env.ASSETS_SERVER_URL}/web/assets/jquery/jquery.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/popper/popper.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/tether/tether.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/bootstrap/js/bootstrap.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/smoothscroll/smooth-scroll.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/dropdown/js/nav-dropdown.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/dropdown/js/navbar-dropdown.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/touchswipe/jquery.touch-swipe.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/viewportchecker/jquery.viewportchecker.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/parallax/jarallax.min.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/ytplayer/jquery.mb.ytplayer.min.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/vimeoplayer/jquery.mb.vimeo_player.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/theme/js/script.js'></script>
  <div id='scrollToTop' class='scrollToTop mbr-arrow-up'><a style='text-align: center;'>
    <i class='mbr-arrow-up-icon mbr-arrow-up-icon-cm cm-icon cm-icon-smallarrow-up'></i></a>
  </div>
  <input name='animation' type='hidden'>
</body>
</html>
"""
  headers = {"content-type": "text/html"}
  return Response(HTML, headers=headers)




def mostrar_success( env, mensaje):

  HTML = f"""<!DOCTYPE html>
<html lang='es-CL' prefix='og: http://ogp.me/ns#'  >
<head>
  <meta charset='UTF-8'>
  <meta http-equiv='X-UA-Compatible' content='IE=edge'>
  <meta name='generator' content='Mobirise v5.1.8, mobirise.com'>
  <meta name='twitter:card' content='summary_large_image'/>
  <meta name='twitter:image:src' content='assets/images/index-meta.png'>
  <meta property='og:image' content='assets/images/index-meta.png'>
  <meta name='twitter:title' content='Eléctrico a Domicilio Providencia'>
  <meta name='viewport' content='width=device-width, initial-scale=1, minimum-scale=1'>
  <link rel='shortcut icon' href='https://alectrico.cl/assets/images/locoalicate-96x155.png' type='image/x-icon'>
  <meta name='description' content='Eléctrico a Domicilio Providencia'>


  <title>Eléctrico a Domicilio Providencia</title>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/web/assets/mobirise-icons2/mobirise2.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/web/assets/mobirise-icons/mobirise-icons.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/tether/tether.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap-grid.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap-reboot.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/dropdown/css/style.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/animatecss/animate.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/socicon/css/styles.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/theme/css/style.css'>
  <link rel='preload' as='style' href='{env.ASSETS_SERVER_URL}/mobirise/css/mbr-additional.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/mobirise/css/mbr-additional.css' type='text/css'>

</head>

<body>

  <section class='menu menu2 cid-sewGNRqCZx' once='menu' id='menu2-2'>
    <nav class='navbar navbar-dropdown navbar-fixed-top navbar-expand-lg'>
      <div class='container'>
        <div class='navbar-brand'>
          <span class='navbar-logo'>
            <a href='https://{env.TLD}.cl'>
              <img src='{env.ASSETS_SERVER_URL}/images/locoalicate-96x155.png' alt='a' style='height: 3rem;'>
            </a>
          </span>
          <span class='navbar-caption-wrap'><a class='navbar-caption text-white text-primary display-4' href='#top'>ALECTRICO</a></span>
        </div>
      </div>
    </nav>
  </section>

  <section class='header1 cid-sewsPSgeos mbr-parallax-background' id='header1-1'>
    <div class='container-fluid'>
        <div class='row justify-content-center'>
            <div class='col-12 col-lg-11'>
              <h1 class='mbr-section-title mbr-fonts-style mb-3 display-4'><strong><em>Eléctricos a Domicilio </em></strong><br><strong><em>- en Providencia -</em></strong></h1>
              <h2 class='mbr-section-subtitle mbr-fonts-style mb-3 display-5'>{env.MISION}</h2>
              <div class='mbr-section-btn mt-3'><a class='btn btn-primary display-4' href='https://wa.me/56945644889'>
              <span class='socicon socicon-whatsapp mbr-iconfont mbr-iconfont-btn'>
              </span></a> <a class='btn btn-info display-4' href='tel:+56932000849'><span class='mobi-mbri mobi-mbri-phone mbr-iconfont mbr-iconfont-btn'></span></a></div>
            </div>
        </div>
    </div>
  </section>

  <section class='mbr-section form4 cid-qAUteatZnl' id='form4-8e' style='border-top-style: solid;border-top-width: 0px;right: -;margin-bottom: 100px;margin-top: 50px;' >
    <div class='container'>
      <h1 class='mbr-section-title mbr-fonts-style mb-3 display-4'><strong><em>{mensaje} </em></strong><br><strong><em>-  Genial!  -</em></strong></h1>
      <div class='row'>
        <div class='offset-3'>
           <img src="icon/success.png" width="150" height="150" alt="success">
        </div>
      </div>
    </div>
  </section>

<section class='barter1 cid-sezOMgUKyB' once='barters' data-bg-video={env.VIDEO_URL} id='barter1-f'>
  <div class='mbr-overlay' style='opacity: 0.6; background-color: rgb(35, 35, 35);'></div>
    <div class='container'>
      <div class='row mbr-white'>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Solo para Ud.</strong></h5>
          <ul class='list mbr-fonts-style display-4'>
            <li class='mbr-text item-wrap'><a href='https://designer.alectrico.cl' class='text-primary'>Designer</a></li>
            <li class='mbr-text item-wrap'><a href='https://registro.alectrica.cl' class='text-primary'>Registro</a></li><li class='mbr-text item-wrap'><a href='https://tips.alectrico.cl' class='text-primary'>Tips</a></li>
          </ul>
        </div>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Reclamos</strong></h5>
            <ul class='list mbr-fonts-style display-4'>
              <li class='mbr-text item-wrap'><a href='https://tico.alectrico.cl' class='text-primary'>tico.alectrico.cl</a></li>
            </ul>
        </div>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Qué es esto?</strong></h5>
          <p class='mbr-text mbr-fonts-style mb-4 display-4'>ALECTRICO<br>Es un lugar de encuentro entre personas con problemas eléctricos y los profesionales que sean capaces de resolverlos.</p>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-3 display-5'>Botones de Pánico<strong></strong></h5>
          <div class='social-row display-7'>

           <div class='soc-item'>
              <a href='https://repair.{env.TLD}.cl' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-cash mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://www.{env.TLD}.cl/agendar' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-edit-2 mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://www.{env.TLD}.cl/agendar'>
                <span class='mbr-iconfont mobi-mbri-setting mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://registro.alectrica,cl' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-user mobi-mbri'></span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
</section>

<script>
  function getLocation() {{ if (navigator.geolocation) {{ navigator.geolocation.getCurrentPosition(showPosition); }} else {{}} }}
  function showPosition(position) {{
    document.getElementById('latitude').value  = position.coords.latitude.toString(10);
    document.getElementById('longitude').value = position.coords.longitude.toString(10); }}
</script>

  <script src='{env.ASSETS_SERVER_URL}/web/assets/jquery/jquery.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/popper/popper.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/tether/tether.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/bootstrap/js/bootstrap.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/smoothscroll/smooth-scroll.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/dropdown/js/nav-dropdown.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/dropdown/js/navbar-dropdown.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/touchswipe/jquery.touch-swipe.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/viewportchecker/jquery.viewportchecker.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/parallax/jarallax.min.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/ytplayer/jquery.mb.ytplayer.min.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/vimeoplayer/jquery.mb.vimeo_player.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/theme/js/script.js'></script>
  <div id='scrollToTop' class='scrollToTop mbr-arrow-up'><a style='text-align: center;'>
    <i class='mbr-arrow-up-icon mbr-arrow-up-icon-cm cm-icon cm-icon-smallarrow-up'></i></a>
  </div>
  <input name='animation' type='hidden'>
</body>
</html>
"""
  headers = {"content-type": "text/html"}
  return Response(HTML, headers=headers)



def agendar( env, mensaje):

  HTML = f"""<!DOCTYPE html>
<html lang='es-CL' prefix='og: http://ogp.me/ns#'  >
<head>
  <meta charset='UTF-8'>
  <meta http-equiv='X-UA-Compatible' content='IE=edge'>
  <meta name='generator' content='Mobirise v5.1.8, mobirise.com'>
  <meta name='twitter:card' content='summary_large_image'/>
  <meta name='twitter:image:src' content='assets/images/index-meta.png'>
  <meta property='og:image' content='assets/images/index-meta.png'>
  <meta name='twitter:title' content='Eléctrico a Domicilio Providencia'>
  <meta name='viewport' content='width=device-width, initial-scale=1, minimum-scale=1'>
  <link rel='shortcut icon' href='https://alectrico.cl/assets/images/locoalicate-96x155.png' type='image/x-icon'>
  <meta name='description' content='Eléctrico a Domicilio Providencia'>


  <title>Eléctrico a Domicilio Providencia</title>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/web/assets/mobirise-icons2/mobirise2.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/web/assets/mobirise-icons/mobirise-icons.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/tether/tether.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap-grid.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/bootstrap/css/bootstrap-reboot.min.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/dropdown/css/style.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/animatecss/animate.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/socicon/css/styles.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/theme/css/style.css'>
  <link rel='preload' as='style' href='{env.ASSETS_SERVER_URL}/mobirise/css/mbr-additional.css'>
  <link rel='stylesheet' href='{env.ASSETS_SERVER_URL}/mobirise/css/mbr-additional.css' type='text/css'>

</head>

<body>

  <section class='menu menu2 cid-sewGNRqCZx' once='menu' id='menu2-2'>
    <nav class='navbar navbar-dropdown navbar-fixed-top navbar-expand-lg'>
      <div class='container'>
        <div class='navbar-brand'>
          <span class='navbar-logo'>
            <a href='https://{env.TLD}.cl'>
              <img src='{env.ASSETS_SERVER_URL}/images/locoalicate-96x155.png' alt='a' style='height: 3rem;'>
            </a>
          </span>
          <span class='navbar-caption-wrap'><a class='navbar-caption text-white text-primary display-4' href='#top'>ALECTRICO</a></span>
        </div>
      </div>
    </nav>
  </section>

  <section class='header1 cid-sewsPSgeos mbr-parallax-background' id='header1-1'>
    <div class='container-fluid'>
        <div class='row justify-content-center'>
            <div class='col-12 col-lg-11'>
              <h1 class='mbr-section-title mbr-fonts-style mb-3 display-4'><strong><em>Eléctricos a Domicilio </em></strong><br><strong><em>- en Providencia -</em></strong></h1>
              <h2 class='mbr-section-subtitle mbr-fonts-style mb-3 display-5'>{env.MISION}</h2>
              <div class='mbr-section-btn mt-3'><a class='btn btn-primary display-4' href='https://wa.me/56945644889'>
              <span class='socicon socicon-whatsapp mbr-iconfont mbr-iconfont-btn'>
              </span></a> <a class='btn btn-info display-4' href='tel:+56932000849'><span class='mobi-mbri mobi-mbri-phone mbr-iconfont mbr-iconfont-btn'></span></a></div>
            </div>
        </div>
    </div>
  </section>

  <section class='mbr-section form4 cid-qAUteatZnl' id='form4-8e' style='border-top-style: solid;border-top-width: 0px;right: -;margin-bottom: 100px;margin-top: 100px;' >
    <div class='container'>
      <h1 class='mbr-section-title mbr-fonts-style mb-3 display-4'><strong><em>{mensaje} </em></strong><br><strong><em></em></strong></h1>
      <div class='row'>

<div class='offset-md-3 col-md-6'>
          <h2 class='pb-3 align-left mbr-fonts-style display-2'>Visita de Electricista a Domicilio</h2>
          <div>
            <div class='icon-block pb-3'>
              <span class='icon-block__icon'>
              <span class='mbri-letter mbr-iconfont'></span>
              </span>
              <h4 class='icon-block__title align-left mbr-fonts-style display-5'>Este servicio tiene un costo de:</h4>
              <div class='col-md-4' data-for='amount'>
                <input type='text' readonly='' value = {env.AMOUNT} class='form-control input' id='amount' name='amount' data-form-field='amount' placeholder='Monto a Pagar' required=''>
              </div>
            </div>
        </div>


        <div class='mbr-section-btn mt-3'><a class='btn btn-primary display-4' href= 'https://api.whatsapp.com/send?phone={env.PUBLICO_COLABORADOR}&text=Hola [.. cuente qué le sucede ..]'> <span class='socicon socicon-whatsapp mbr-iconfont mbr-iconfont-btn'></span></a> 
           <h1 class='mbr-section-title mbr-fonts-style mb-3 display-4'><strong><em>Continuar en Whatsapp</em></strong><br><strong><em>- Requiere Android Ver. 6 o más reciente -</em></strong></h1>


        <div data-form-type="formoid">

          <form class="block mbr-form" action="https://www.alectrico.cl/agendar" method="get" data-form-title="Agendar Form">
            <div class="row">
              <div class="col-md-6 multi-horizontal" data-for="nombre">
                <input type="text" class="form-control input" name="nombre" data-form-field="Name" placeholder="Su nombre" required="" id="name-form4-8e">
              </div>
              <div class="col-md-6 multi-horizontal" data-for="fono">
                <input type="text" class="form-control input" name="fono" data-form-field="Fono" placeholder="Fono" required="" id="phone-form4-8e">
              </div>
              <div class="col-md-8" data-for="email">
                <input type="email" class="form-control input" name="email" data-form-field="Email" placeholder="Email" required="" id="email-form4-8e">
              </div>
              <div class="col-md-4" data-for="comuna">
                <input type="text" class="form-control input" name="comuna" data-form-field="Comuna" placeholder="Comuna" required="" id="comuna-form4-8e" value='Providencia'>
              </div>
              <div class="col-md-12" data-for="descripcion">
                <textarea class="form-control input" name="descripcion" rows="3" data-form-field="Descripcion" placeholder="Describa su problema" style="resize:none" required="" id="message-form4-8e"></textarea>
              </div>
              <div class="container">
                <iframe frameborder="0" style="border:0;width:525; height:400" src="https://www.google.com/maps/embed/v1/place?key=AIzaSyCx3d07zxHPLvkFBLlAR3Ng8a9wsAsGoJ8&amp;q=place_id:ChIJ92aDbnzPYpYRfI1HCsD874c" allowfullscreen="">
                </iframe>
              </div>
              <div class="col-md-12" data-for="direccion">
                <textarea class="form-control input" name="direccion" rows="3" data-form-field="Direccion" placeholder="Escriba la dirección del lugar en Providencia, donde se requiere un eléctrico" required="" style="resize:none" id="message-form4-8f"></textarea>
              </div>
              <div  onclick="getLocation()"  class="input-group-btn col-md-4" style="margin-top: 1px;">
               <button href="" type="button" class="btn btn-secondary btn-form display-4">Agregar mi ubicación:</button>
              </div>

              <div class="col-md-4" data-for="latitude">
                <input type="text" readonly="" class="form-control input" id="latitude" name="latitude" data-form-field="latitude" placeholder="Latitud" required="" value=''>
              </div>
              <div class="col-md-4" data-for="longitude">
                <input type="text" readonly="" class="form-control input" id="longitude" name="longitude" data-form-field="longitude" placeholder="Longitud" required="" value=''>
              </div>
              <div class="col-md-4" data-for="amount">
                <input type="text" readonly="" hidden="" value = {env.AMOUNT} class="form-control input" id="amount" name="amount" data-form-field="amount" placeholder="Monto a Pagar" required="">
              </div>

              <div class="input-group-btn col-md-12" style="margin-top: 10px;"><button href="" type="submit" class="btn btn-primary btn-form display-4">Agendar</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</section>


<section class='barter1 cid-sezOMgUKyB' once='barters' data-bg-video={env.VIDEO_URL} id='barter1-f'>
  <div class='mbr-overlay' style='opacity: 0.6; background-color: rgb(35, 35, 35);'></div>
    <div class='container'>
      <div class='row mbr-white'>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Solo para Ud.</strong></h5>
          <ul class='list mbr-fonts-style display-4'>
            <li class='mbr-text item-wrap'><a href='https://designer.alectrico.cl' class='text-primary'>Designer</a></li>
            <li class='mbr-text item-wrap'><a href='https://registro.alectrica.cl' class='text-primary'>Registro</a></li><li class='mbr-text item-wrap'><a href='https://tips.alectrico.cl' class='text-primary'>Tips</a></li>
          </ul>
        </div>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Reclamos</strong></h5>
            <ul class='list mbr-fonts-style display-4'>
              <li class='mbr-text item-wrap'><a href='https://tico.alectrico.cl' class='text-primary'>tico.alectrico.cl</a></li>
            </ul>
        </div>
        <div class='col-12 col-md-6 col-lg-3'>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-2 display-7'><strong>Qué es esto?</strong></h5>
          <p class='mbr-text mbr-fonts-style mb-4 display-4'>ALECTRICO<br>Es un lugar de encuentro entre personas con problemas eléctricos y los profesionales que sean capaces de resolverlos.</p>
          <h5 class='mbr-section-subtitle mbr-fonts-style mb-3 display-5'>Botones de Pánico<strong></strong></h5>
          <div class='social-row display-7'>

           <div class='soc-item'>
              <a href='https://repair.{env.TLD}.cl' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-cash mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://www.{env.TLD}.cl/agendar' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-edit-2 mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://www.{env.TLD}.cl/agendar'>
                <span class='mbr-iconfont mobi-mbri-setting mobi-mbri'></span>
              </a>
            </div>
            <div class='soc-item'>
              <a href='https://registro.alectrica,cl' target='_blank'>
                <span class='mbr-iconfont mobi-mbri-user mobi-mbri'></span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
</section>

<script>
  function getLocation() {{ if (navigator.geolocation) {{ navigator.geolocation.getCurrentPosition(showPosition); }} else {{}} }}
  function showPosition(position) {{
    document.getElementById('latitude').value  = position.coords.latitude.toString(10);
    document.getElementById('longitude').value = position.coords.longitude.toString(10); }}
</script>

  <script src='{env.ASSETS_SERVER_URL}/web/assets/jquery/jquery.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/popper/popper.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/tether/tether.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/bootstrap/js/bootstrap.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/smoothscroll/smooth-scroll.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/dropdown/js/nav-dropdown.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/dropdown/js/navbar-dropdown.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/touchswipe/jquery.touch-swipe.min.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/viewportchecker/jquery.viewportchecker.js'></script> 
  <script src='{env.ASSETS_SERVER_URL}/parallax/jarallax.min.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/ytplayer/jquery.mb.ytplayer.min.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/vimeoplayer/jquery.mb.vimeo_player.js'></script>  
  <script src='{env.ASSETS_SERVER_URL}/theme/js/script.js'></script>
  <div id='scrollToTop' class='scrollToTop mbr-arrow-up'><a style='text-align: center;'>
    <i class='mbr-arrow-up-icon mbr-arrow-up-icon-cm cm-icon cm-icon-smallarrow-up'></i></a>
  </div>
  <input name='animation' type='hidden'>
</body>
</html>
"""
  headers = {"content-type": "text/html"}
  return Response(HTML, headers=headers)
























#Actuliza los fonos en la landing page
def fonos( env):
   headers = {  'Access-Control-Allow-Origin'      :'*',
                'Access-Control-Allow-Credentials' : True,
                'content-type'                     : 'application/json'
   }

   body_json = { "fonos" :
        { "colaborador": { "publico" : "colaborador",
                           "numero"  : str(env.PUBLICO_CLIENTE), 
                           "html"    : str(env.PUBLICO_CLIENTE_HTML)
                         },
              "cliente": { "publico" : "cliente",
                           "numero"  : str(env.PUBLICO_COLABORADOR),
                           "html"    : str(env.PUBLICO_COLABORADOR_HTML)
                         }
      }
   }
   return Response.json(body_json, headers=headers, status='200' )

