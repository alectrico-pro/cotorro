
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



#importatnte, envia un formulario
async def enviar_template_say_visita_flow_reserva( request, env, fono):
        console.log("En enviar_template say_visita -> flow reserva")
        imagen_url = f"{env.API_URL}/{env.LOGUITO_PATH}"
        uri        = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {await env.META.get('COTORRO_TOKEN')}"
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
             "Authorization": f"Bearer {await env.META.get('AE_TOKEN')}",
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


    #--------------------  PRESENTA UN FORMULARIO QUE TERMINA EN AGENDAR ----------
    elif url.path == '/':
        return agendar(env, 'Ingrese su número de Whatsapp para recargar Créditos de Atención en Alectrico')
    #-----------------------------------------------------------------------------------

    #Esos formularios son un poco diferentes a los usuales usan un assets llamado formoide en las
    #landing_pages

       #agendar?nombre=oipoi+upoi&fono=987654321&email=hjhkjh%40lkjlkj.ll&comuna=Providencia&descripcion=lkñ+jñlkj&direccion=o+ṕoiṕoiṕo&latitude=&longitude=&amount=68000
    elif url.path == '/listar':
        console.log("En listar")
        colaboradores = await env.NOMINA.list(prefix = "activo:")

        keys = [key_info.name for key_info in colaboradores.keys]
        console.log(f"keys {keys}")
        return success_mostrar_fono( env, f"colaboradores {keys}", 'colaboradores')

    elif url.path == '/recargar':
        console.log(f"Params en /agendar {params}")
        buy_order   = str( random.randint(1, 10000))
        fono        = params['fono'][0]
        amount      = params['amount'][0]
        cantidad    = params['cantidad'][0]

        total       = int( amount ) * int( cantidad )

        #no se envía el cuestionario, porque se vería repetido
        #await enviar_template_say_visita_flow_reserva(request, env, fono )
        await say_jefe( env, f"en recargar {fono}")

        #En este llamado el argumento session_id se toma como fono
        #Eso es porque uso la defininción de transbank para enviar el fono
        #Porque lo necesito en def tbk_commit para enviar el voucher al cliente
        token_ws, uri = await genera_link_de_pago_tbk( buy_order, total, env.RETURN_URL, fono, env)
        await anotar_tokens( env, buy_order, fono, amount, int(cantidad) )
        return pedir_confirmacion_de_pago(request, env, buy_order, total, uri, token_ws)


    #--------------------------------------------------------------------------------------------

    #------------------------------------------ PAGO EN PASARELA TRANSBANK --------------------
    #Este es al paso previo antes de redirigiar a tranbank
    #Desde allá vuelve a return_url
    #Pero con diferentes argumentos
    elif (url.path.startswith( "/transbank")  or url.path.startswith( '/%7B%7B1%7D%7D/transbank') )   and method == 'GET':
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
   #--------------------------------------------------------------------------------------------



    #----------------- WEBHOOK DE WABA ---------------------------------------------------------
    elif url.path.startswith("/webhook"): # or url.path.startswith("/api/v1/santum/webhook"):
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
               descripcion = value.messages[0].text.body
               id          = value.messages[0].id
               wa_id       = request_json.entry[0].changes[0].value.contacts[0].wa_id
               buy_order   = str( random.randint(1, 10000))

               #await save_text_message(env, id, wa_id, buy_order, descripcion, amount)

               path_de_pago = f"/transbank?amount={env.PRECIO_PROCESO}&session_id={wa_id}&buy_order={buy_order}"
               try:
                 await say_link_de_pago( env, wa_id, '\uD83D\uDE01',  env.PRECIO_PROCESO, path_de_pago )
               except:
                 pass

               await difundir_a_colaboradores(env, buy_order, 'no-indica', descripcion, 'no-indica', wa_id, 'user@alectrico.cl', 'no-indica', env.PRECIO_TOKEN)


               #no puedo difundir_a_colaboradores aquí porque el cliente no ha introducido datos
               #envío al cuestionario flow para obtener los datos
             
               await enviar_template_say_visita_flow_reserva( request, env, wa_id )
               #await say_jefe(env, f"Hola Jefe, alguien escribió: {body}----{wa_id}" )
               return Response( "Procesado", status="200")

               
            console.log(f"Es un mensaje y nada más: {value.messages[0]}")
            return Response( "no procesado", status="200")



        elif hasattr(value, 'statuses') == True :
            console.log("Es un statuses")
            status = value.statuses[0].status
            id     = value.statuses[0].id

            console.log(status)
            #Guardando el status para futura referencia
            #await save_status(env, id, status )

            #ya no estoy vigilando failed,
            #Solo envío el cuestiari y el link de pago al comienzo
            match status:
                 case 'failed':
                    #Busco el objeto que ha fallado
                    resultado = await env.FINANCIERO.get(str(id) )
                     
                    #Compruebo que haya sido un fallo al enviar el template say_visita
                    #Verifico que el error sea de Message undeliverable 
                    #Eso cubre a los fonos inexisentes, redes que no funcionan con waba
                    #Y versiones de androide menores a la exigida para esa característica de cuestionarios
                     
                    if resultado == 'say_visita -> flow reserva' and value.statuses[0].errors[0].title == 'Message undeliverable':
                           #Intento eliminar el registro de este envío fallido
                           #De esa forma evito que se vuelva a reaccionar sobre lo mismo, más adelante
                           #Se usa try porque el kv_name está limitado a 1000 operaciones diarias
                           #Si falla algo aquí no podré otorgar Response 200
                           try:
                              await env.FINANCIERO.delete(str(id))
                           except:
                              await save_status(env, id, 'failed' )

                           wa_id        = request_json.entry[0].changes[0].value.statuses[0].recipient_id
                           buy_order    = str( random.randint(1, 10000))
                           direccion    = 'no indica'
                           comuna       = 'no indica'
                           descripcion  = 'no indica'
                           email        = 'user@alectrico.cl'
                           name         = 'no indica'
                           amount       = env.PRECIO_VISITA

                           try:
                             await guardar_token( env, buy_order, wa_id, name, email, direccion, comuna, descripcion, amount)
                           except:
                             pass

                           path_de_pago = f"/transbank?amount={amount}&session_id={wa_id}&buy_order={buy_order}"
                           try:
                             await say_pagar_visita( env, wa_id, '\uD83D\uDE01', amount, path_de_pago )
                           except:
                             pass

            return Response( "ok", status="200")


    #----------------------------------------------------------------------------------------


    else:     
      console.log("No se ha identificado")
      return mostrar_not_found(env, "Bah! Ocurrió un Error")
#----------------------------FIN llegada de requests --------------------------


#.......................... MENU PRINCIPAL -----------------------------------
#-----------------------------------------------------------------------------
#@app.route("/webhook", methods=["GET"])
#Hay que hacerlo nuevamente. Se me borró el que usé al comienzo
def webhook_get(request, env):
    console.log("En webhook_get")
    if params["hub.mode"] == ['subscribe'] and params['hub.verify_token'] == env.VERIFY_TOKEN:
        return Response(params['hub.challenge'][0], status=200)
    else:
        return Response("Error", status=403)


#----------------------------- FUNCIONES ------------------------------------------------------


async def save_text_message( env, id, fono, buy_order, descripcion, amount ):
    await env.FINANCIERO.put( str(buy_order), json.dumps( {"pedido": { "email": "user@alectrico.cl", "fono": fono, 'buy_order': buy_order, 'descripcion': descripcion, 'amount': amount }}), { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION } )
    return




async def anotar_tokens( env, buy_order, fono, amount, cantidad ):
    now = datetime.now()
    fecha_en_el_vencimiento = now + timedelta(days = env.VENCIMIENTO_TOKEN_DIAS)
    for orden in range(1, cantidad + 1 ):
      orden = str( random.randint(1, 10000))
      pedido = { 'token': {'orden': orden, 'expira_en': str(fecha_en_el_vencimiento), 'buy_order': buy_order, 'fono': fono, "amount": amount, "acuñado_en": json.dumps( date.today().isoformat()) }}
      await env.FINANCIERO.put( f"{fono}:{buy_order}:token:{ datetime.timestamp(now)}:{orden}", json.dumps(pedido), { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION })
    return


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
   await anotar_pago( env, response_json)
   await pagar_tokens( env, response_json.session_id, response_json.buy_order)
   await say_jefe(env, f"Pagado {response_json.buy_order}----{response_json.session_id}" )
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


async def anotar_pago( env, response_json):
   console.log(f"response_json {response_json}")
   reply = to_markdown( response_json )
   console.log(f"reply {reply}")
   await env.FINANCIERO.put( f"{response_json.session_id}:{response_json.buy_order}:pago", reply, { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION })
   return await send_reply(env, response_json.session_id, reply)


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



#este aviso podría mejorarse , pero como es una comuniación interna lo he dejado así
async def say_jefe(env, descripcion):
        return await say_tomar( env, str(env.FONO_JEFE), 'ALE JEFE', descripcion, 'PROVIDENCIA')


#este aviso podría mejorarse , pero como es una comuniación interna lo he dejado así
async def derivar_jefe(env, nombre, descripcion, direccion, buy_order, comuna):
        return await say_atender(env, str(env.FONO_JEFE), nombre, direccion, comuna, buy_order)



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
                "Authorization": f"Bearer {await env.META.get('AE_TOKEN')}"
        }
        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {await env.META.get('AE_TOKEN')}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return



async def pagar_tokens(env, fono, buy_order):
        now = datetime.now()

        console.log("En actualizar saldos")
        console.log(f"Fono {fono}")
        console.log(f"buy_order {buy_order}")
        list_options = {"prefix": f"{fono}:{buy_order}:"}
        console.log(f"list_options {list_options}")
        lista = await env.FINANCIERO.list( prefix = f"{fono}:{buy_order}")
        if len( lista.keys ) >= 2:
           for key in lista.keys:
             console.log(f"key name {key.name}")
             if key.name.endswith("pago"):
                console.log("Encontrado pago")
                tokens = await env.FINANCIERO.list( prefix = f"{fono}:{buy_order}:token" )
                if len( tokens.keys ) > 0:
                   console.log(f"Encontrado token")
                   for key in tokens.keys:
                     token = await env.FINANCIERO.get( key.name )
                     token_dict = json.loads(token)
                     expira_en  = token_dict['token']['expira_en']
                     orden      = token_dict['token']['orden']
                     console.log(f"expira en {expira_en}")
                     if datetime.today() > datetime.fromisoformat( expira_en ):
                       await env.FINANCIERO.put(f"{fono}:token:pagado:expirado:{orden}", token)
                     else:
                       await env.FINANCIERO.put(f"{fono}:token:pagado:no_expirado:{datetime.timestamp( datetime.fromisoformat( expira_en ))}:{orden}", token)

                     await env.FINANCIERO.delete( F"{key.name}" )
     
        #colaboradores_string = await env.NOMINA.get('colaboradores')
        #colaboradores   = json.loads( colaboradores_string)
        #for colaborador in colaboradores:
        #   console.log(f"colaborador {colaborador}")

        return



async def send_message( env, wa_id, msg):
        console.log( "En send_message")
        console.log(f"wa_id {wa_id}")
        console.log( f"msg  {msg}")

        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {await env.META.get('AE_TOKEN')}"
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
                 "Authorization": f"Bearer {await env.META.get('AE_TOKEN')}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return Response( msg, status="200")


#sujeto a eror de reenganche en waba
#Hay que usar un template que acepte el texto
#con
async def send_reply( env, wa_id, reply):

        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {await env.META.get('AE_TOKEN')}"
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
                 "Authorization": f"Bearer {await env.META.get('AE_TOKEN')}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result{result}")
        return Response( reply, status="200")


#Funciona para android > 5
#Muestra un aviso de que se le cobrará un amount
#Y al presionar Pagar
#Se va a Transbank
def pedir_confirmacion_de_pago(request, env, buy_order, amount, pago_url, token_ws):
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

              <div class='mbr-section-btn mt-3'>
              <a class='btn btn-primary display-4' href='https://wa.me/56945644889'>
              <span class='socicon mbr-iconfont mbr-iconfont-btn'>REINTENTAR</span>
              </a> 
              </div>
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




def success_mostrar_fono( env, mensaje, fono):

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
              <div class='mbr-section-btn mt-3'><a class='btn btn-primary display-4' href='https://wa.me/56{fono}'>
              <span class='socicon socicon-whatsapp mbr-iconfont mbr-iconfont-btn'>
              </span></a> <a class='btn btn-info display-4' href='tel:{fono}'><span class='mobi-mbri mobi-mbri-phone mbr-iconfont mbr-iconfont-btn'></span></a></div>
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
          <h2 class='pb-3 align-left mbr-fonts-style display-2'>Recarga Token Bat</h2>
          <div>
            <div class='icon-block pb-3'>
              <span class='icon-block__icon'>
              <span class='mbri-letter mbr-iconfont'></span>
              </span>
              <h4 class='icon-block__title align-left mbr-fonts-style display-5'>Este servicio tiene un costo de:</h4>
              <div class='col-md-4' data-for='amount'>
                <input type='text' readonly='' value = {env.PRECIO_TOKEN} class='form-control input' id='amount' name='amount' data-form-field='amount' placeholder='Monto a Pagar' required=''>
              </div>
            </div>
        </div>


        <div data-form-type="formoid">

          <form class="block mbr-form" action="https://recarga.alectrico.cl/recargar" method="get" data-form-title="Agendar Form">
            <div class="row">
              <div class="col-md-6 multi-horizontal" data-for="fono">
                <input type="text" class="form-control input" name="fono" data-form-field="Fono" placeholder="Fono" required="" id="phone-form4-8e">
              </div>

              <div class="col-md-6 multi-horizontal" data-for="cantidad">
                <input type="number" class="form-control input" name="cantidad" data-form-field="Fono" placeholder="Cantidad" required="" id="phone-form4-8e">
              </div>

              <div class="col-md-6 multi-horizontal" data-for="nombre">
                <input type="text" class="form-control input" hidden="" name="nombre" data-form-field="Name" placeholder="Su nombre" id="name-form4-8e">
              </div>

              <div class="col-md-8" data-for="email">
                <input type="email" class="form-control input" hidden="" name="email" data-form-field="Email" placeholder="Email" id="email-form4-8e">
              </div>
              <div class="col-md-4" data-for="comuna">
                <input type="text" class="form-control input" hidden="" name="comuna" data-form-field="Comuna" placeholder="Comuna" id="comuna-form4-8e" value='Providencia'>
              </div>
              <div class="col-md-12" data-for="descripcion">
                <textarea class="form-control input" hidden="" name="descripcion" rows="3" data-form-field="Descripcion" placeholder="Describa su problema" style="resize:none" id="message-form4-8e"></textarea>
              </div>

              <div class="col-md-12" data-for="direccion">
                <textarea class="form-control input" hidden="" name="direccion" rows="3" data-form-field="Direccion" placeholder="Escriba la dirección del lugar en Providencia, donde se requiere un eléctrico" style="resize:none" id="message-form4-8f"></textarea>
              </div>

              <div class="col-md-4" data-for="amount">
                <input type="text" readonly="" hidden="" value = {env.PRECIO_TOKEN} class="form-control input" id="amount" name="amount" data-form-field="amount" placeholder="Monto a Pagar" required="">
              </div>

              <div class="input-group-btn col-md-12" style="margin-top: 10px;"><button href="" type="submit" class="btn btn-primary btn-form display-4">Recargar</button>
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


























