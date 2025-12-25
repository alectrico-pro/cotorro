#https://developers.cloudflare.com/pages/tutorials/use-r2-as-static-asset-storage-for-pages/
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


#-3¿import clips
#$$https://pyodide.org/en/stable/usage/loading-packages.html
#Installing packages

#Pyodide supports installing following types of packages with micropip,

#    pure Python wheels from PyPI with micropip.

#    pure Python and binary wasm32/emscripten wheels (also informally known as “Pyodide packages” or “packages built by Pyodide”) from the JsDelivr CDN and custom URLs. micropip.install() is an async Python function which returns a coroutine, so it need to be called with an await clause to run.

#import clips no funciona, a pesar de que el package se carga bien

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

#Para decodificar flows endpoint
import os
from base64 import b64decode, b64encode


#from fpdf import FPDF
#pdf = FPDF()
#pdf.add_page()
#pdf.set_font("Arial", size=12)
#pdf.cell(200, 10, txt="Go Be Great!", ln=1, align="C")
#pdf.output("C:/Temp/sample_demo.pdf")




from itertools import count

id_generator = count(start=1)  # Starts from 1, increments by default

#criyptography es un paquete oficial de pyodide
#from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1, hashes
#from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
#from cryptography.hazmat.primitives.serialization import load_pem_private_key


#Envía un mensaje a usuarios fuera de la ventana
async def send_aviso( env, fono, mensaje):
        console.log("En send_aviso")

        imagen_url       = f"{env.API_URL}/{env.LOGUITO_PATH}"
        phone_id         = await env.AI_NUMBER_ID.get('AI_NUMBER_ID')
        bearer           = await env.AI_GALLEGO_USER_TOKEN.get('AI_GALLEGO_USER_TOKEN')
        console.log(f"phone_id {phone_id} bearer {bearer} fono {fono} mensaje {mensaje} imagen_url {imagen_url}" )
        uri        = f"https://graph.facebook.com/v24.0/{phone_id}/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}"
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
             "Authorization": f"Bearer {bearer}",
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



async def get_bearer_and_phone(env, cliente ):
  if cliente == True:
    console.log("usando el user token de cliente")
    bearer   = await env.AE_REPAIR_USER_TOKEN.get('AE_REPAIR_USER_TOKEN')
    phone_id = env.CLIENT_PHONE_NUMBER_ID
  else:
    console.log("usando el user token de colaborador COTORRO_EXO_USER_TOKEN")
    bearer    = await env.COTORRO_EXO_USER_TOKEN.get('COTORRO_EXO_USER_TOKEN')
    phone_id = env.PHONE_NUMBER_ID
  return bearer, phone_id

async def xxx( env, wa_id):
                          fono = fix_fono( wa_id )
                          dico =  {
                                       'max_tokens': 502,
                                       'messages': [
                                              { 'role': 'user',   'content': 'xxx'}
                                                   ]}
                          #Llamo al LLM para que se imponga del resultado 
                          result = await env.AI.run(await env.I.get('MODELO'), to_js (dico ) )
 
                          mensajes = await env.DIALOGO.list( prefix = f"{fono}")
                          if  mensajes:
                            for key in mensajes.keys:
                                 await env.DIALOGO.delete( key.name)
                          reply = (
                          f"Su chat con el el bot ha sido borrado. \n"
                          )
                          await send_reply(env, wa_id,  reply, True )
                          return Response( "Borrado Dialogo para fono", status="200")



def data(request):
    try:
        # Parse the request body
        body = json.loads(request.body)

        # Read the request fields
        encrypted_flow_data_b64 = body['encrypted_flow_data']
        encrypted_aes_key_b64 = body['encrypted_aes_key']
        initial_vector_b64 = body['initial_vector']

        decrypted_data, aes_key, iv = decrypt_request(
            encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64)
        print(decrypted_data)

        # Return the next screen & data to the client
        response = {
            "screen": "SCREEN_NAME",
            "data": {
                "some_key": "some_value"
            }
        }

        # Return the response as plaintext
        return HttpResponse(encrypt_response(response, aes_key, iv), content_type='text/plain')
    except Exception as e:
        print(e)
        return JsonResponse({}, status=500)

def decrypt_request(encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64):
    flow_data = b64decode(encrypted_flow_data_b64)
    iv = b64decode(initial_vector_b64)

    # Decrypt the AES encryption key
    encrypted_aes_key = b64decode(encrypted_aes_key_b64)
    private_key = load_pem_private_key(
        PRIVATE_KEY.encode('utf-8'), password=None)
    aes_key = private_key.decrypt(encrypted_aes_key, OAEP(
        mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

    # Decrypt the Flow data
    encrypted_flow_data_body = flow_data[:-16]
    encrypted_flow_data_tag = flow_data[-16:]
    decryptor = Cipher(algorithms.AES(aes_key),
                       modes.GCM(iv, encrypted_flow_data_tag)).decryptor()
    decrypted_data_bytes = decryptor.update(
        encrypted_flow_data_body) + decryptor.finalize()
    decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))
    return decrypted_data, aes_key, iv


def encrypt_response(response, aes_key, iv):
    # Flip the initialization vector
    flipped_iv = bytearray()
    for byte in iv:
        flipped_iv.append(byte ^ 0xFF)

    # Encrypt the response data
    encryptor = Cipher(algorithms.AES(aes_key),
                       modes.GCM(flipped_iv)).encryptor()
    return b64encode(
        encryptor.update(json.dumps(response).encode("utf-8")) +
        encryptor.finalize() +
        encryptor.tag
    ).decode("utf-8")


#------------------------------------------------ FLOW ENDPOINT ---

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
def get_next_id():
    return str( next(id_generator))


def to_js(obj):
    return _to_js(obj, dict_converter=Object.fromEntries)

# gather_response returns both content-type & response body as a string
async def gather_response(response):
    headers = response.headers
    content_type = headers["content-type"] or ""
    if "application/json" in content_type:
        return (content_type, json.dumps(dict(await response.json())))
    return (content_type, await response.text())


async def activar( env, fono):
        fono = fix_fono( fono )
        name = "inactivo:" + str(fono)
        value = await env.NOMINA.get( name )
        if value:
          await env.NOMINA.put( "activo:" + str(fono), value )
          await env.NOMINA.delete( name )
          reply = (
           f"{fono} ha sido activado.\n"
           "recibirá avisos de trabajos!\n"
          )
        else:
         reply = (
          f"{fono} no es de un colaborador inactivo \n"
          "No se pudo activar"
         )
        await send_reply( env, fono, reply, False)


async def desactivar( env, fono):
        fono = fix_fono( fono )
        name =  "activo:" + str( fono ) 
        value = await env.NOMINA.get( name )
        if value:
          await env.NOMINA.put( "inactivo:" + str( fono) , value )
          await env.NOMINA.delete( name )
          reply = (
           f"{fono} ha sido desactivado.\n"
           "Ya no recibirá más avisos. \n"
           "Sus tokens permanecerán. \n"
          )
        else:
         reply = (
          f"{fono} no está activo. No se pudo desactivar"
         )
        await send_reply( env, fono, reply, False)


async def desuscribir( env, fono):
        fono = fix_fono( fono )
        name = "inactivo:" + str(fono)
        value = await env.NOMINA.get( name )
        if value:
          await env.NOMINA.delete( name )
          reply = (
           f"{fono} ha sido desuscrito.\n"
           "ya no recibirá avisos de trabajos!\n"
           "tampoco lo podrá activar por Whatsapp \n"
           "sus tokens no se tocarán por si decide volver \n"
          )
        else:
         reply = (
          f"{fono} no es de un colaborador inactivo \n"
          "No se pudo desuscribir"
         )
        await send_reply( env, fono, reply, False)



async def suscribir( env, fono, nombre):
        fono = fix_fono( fono )
        name = "activo:" + str(fono)
        value = await env.NOMINA.get( name )
        if not value:
          await env.NOMINA.put("activo:" + str(fono), json.dumps( {"nombre":nombre, "fono": fono }) )
          reply = (
           f"{nombre}\n"
           f"{fono} ha sido suscrito.\n"
           f"a la plataforma alectrico ® repair\n"
           "desde ahora recibirá avisos de trabajos!\n"
          )
        else:
         reply = (
          f"{fono} ya se usa por un colaborador activo \n"
          "No se pudo suscribir"
         )
        await send_reply( env, fono, reply, False)



#importatnte, envia un template say_test_data_1 que llama al flow
#test_TDA_1
#OJO: Es de marketing
async def enviar_concurso( env, fono, nombre):
        console.log("En enviar_template say_test_tda_1 -> flow test_TDA_1")
        imagen_url = f"{env.API_URL}/{env.CONCURSO_PATH}"

        bearer, phone_id = await get_bearer_and_phone(env, False)

        uri        = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
        body = {
          "messaging_product": "whatsapp",
          "to": f"{fono}",
          "type": "template",
          "template": {
            "name": "say_test_tda_1",
            "language": {
              "code": "es"
          },
          "components": [
                   { "type": "body",
                     "parameters": [
                         { "type": "text", "parameter_name": "nombre", "text": nombre },
                     ]
                   },

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
             "Authorization": f"Bearer {bearer}",
             "content-type": "application/json;charset=UTF-8"
           },
        }
        #--- anota que se envió un flow cuestionario, porque podría darse como failed
        response = await fetch(uri, to_js(options))
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        result_dict = json.loads( result )
        id = result_dict['messages'][0]['id']
        console.log(f"id {id}")
        try:
          await env.BUY_ORDER.put( id, 'say_visita -> flow test_TDA_1', { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION } )
        except:
          pass
        #---------------------------------------------------------------------------------------
        return Response( 'ok', status="200")


#-------------------------------------------------  BEGIN AI -----------------------------------------------------
#No tengo la función Blog 
#async def sec_to_markdown():
#      pdf = await env.R2.get("RIC-N04-Conductores-y-Canalizaciones_removed.pdf")

#      await env.AI.toMarkdown([
#        {
#          "name": "sec.pdf",
#          "blob": new Blob([await pdf.arrayBuffer()], {
#            "type": "application/octet-stream",
#          }),
#        },
#      ])
    

async def canal_colaborador_ai(env, wa_id, descripcion ):
                    console.log(f"{wa_id} es colaborador")
                    buy_order   = str( random.randint(1, 10000))
                    #await save_text_message(env, id, wa_id, buy_order, descripcion, amount)

                    #path_de_pago = f"/transbank?amount={env.PRECIO_PROCESO}&session_id={wa_id}&buy_order={buy_order}"
                    #try:
                    # await say_link_de_pago( env, wa_id, '\uD83D\uDE01',  env.PRECIO_PROCESO, path_de_pago )
                    #except:
                    # pass
                    result = await env.AI.run(await env.I.get('MODELO'), to_js(
                    { 'messages': [
                    { 'role': 'system', 'content': """Te llamas Alam Brito y eres asistente de la plataforma alectrico® exo!. Explica que alectrico exo! es una plataforma para electricistas y otro colaboradores, los cuales reciben avisos de trabajos. Esos avisos los pueden tomar si tienen tokens. La plataforma responde a los siguientes comandos:

/suscribir: Para estar como colaborador
/activar: Para recibir avisos
/desactivar: Para dejar de recibir avisos
/comprar_tokens: Para comprar un token

No responderás consultas concretas sobre los pliegos SEC RIC 1 al RIC 6 y el RIC 18 a menos que el electricista tenga saldo a favor. Solo en ese caso. """ },
                    { 'role': 'electricista', 'content': descripcion } ],} ) );

                    console.log(f"{result.response}")
                    reply = (
                     f"{result.response} \n"
                     "..................... \n "
                     "Escriba *xxx* para terminar \n "
                    )
                    #await send_reply(env, env.FONO_JEFE,  reply )
                    await send_reply(env, wa_id,  reply, False )

                    #await difundir_a_colaboradores(env, buy_order, nombre, descripcion, 'no-indica' , wa_id, 'user@alectrico.cl', 'no-indica', env.PRECIO_TOKEN)

                    #await difundir_a_colaboradores(env, buy_order, nombre, descripcion, comuna, fono, email, direccion, env.PRECIO_TOKEN)

                    #no puedo difundir_a_colaboradores aquí porque el cliente no ha introducido datos
                    #envío al cuestionario flow para obtener los datos

                    #await enviar_template_say_visita_flow_reserva( request, env, wa_id )
                    #await say_jefe(env, f"Hola Jefe, alguien escribió: {body}----{wa_id}" )
                    return Response( "Ud. es Colaborador", status="200" )


#---- atiende a los colaboradores en temas normativos sec
#WIP
async def alambrito( env, wa_id, prompt ):
      console.log("Estoy en alambrito")
      answer = await env.AI.autorag("square-cloud-8e93").aiSearch( to_js(
      {
      "query": prompt, "model": "@cf/meta/llama-3.3-70b-instruct-fp8-fast", "rewrite_query": True, "max_num_results": 2, "ranking_options": { "score_threshold": 0.3  }}))

      console.log(f"{answer.response}")
      reply = (
      "*alectrico®* -- Alam Brito ai\n"
      ".............................\n"
      f"{answer.response} \n"
      "..................... \n "
     "alectrico® exo!\n "
      )
      await send_reply(env, wa_id,  reply, False )
      return answer.response


#---- atiende a los clientes de alectrico -- fono  932000849
async def alexo( env, request, wa_id, descripcion, nombre):
                      console.log("Entrando en alexo")
                      console.log(f"Trabajando con la descripcion {descripcion}")

                      fono = fix_fono(wa_id)
                      mensajes_anteriores = await env.DIALOGO.list( prefix = f"{ fono }:no_colaborador" )
                      k = len ( mensajes_anteriores.keys)
                      if k == 0:
                        buy_order   = str( random.randint(1, 10000))
                        #await save_text_message(env, id, wa_id, buy_order, descripcion, amount)
                        path_de_pago = f"/transbank?amount={env.PRECIO_PROCESO}&session_id={wa_id}&buy_order={buy_order}"


                        console.log("No hay mensajes en DIALOGO")
                        #resentacion = await env.INDUCCION_ALEXO.get() 


                        #Guía para cuando se use LLAMA
                        #REF: https://www.llama.com/docs/how-to-guides/prompting/



                        #prompt 01
                        prompt_01="""Te llamas alexo y eres el asistente de la plataforma alectrico, la cual contacta en Providencia, Chile a las personas con electricistas a domicilio.
En primero lugar debes conseguir una ficha con los siguientes datos:

1. Problema: Descripción de su problema eléctrico
2. Nombre
3. Teléfono
4. Comuna
5. Dirección
6. email

Debes preguntar si el cliente quisiera que le sugieran un electricista, o sí prefiere elegirlo de una lista o si prefiere llenar un cuestionario detallado que será envíado a los electricistas interesados. Debes llenar una ficha con los siguientes datos: nombre: Nombre de la persona que recibirá al electricista, comuna: Comuna hacia donde se deba dirigir el electricista, dirección: Dirección del lugar donde se reporta el problema, descripción: Descripción del problema, fono: Teléfono de contacto al que debe llamar el electricista, email: Dirección de correo electrónico para recibir el contrato y cualquier otra documentación. Cuando tengas la ficha completa, debes mostrársela al cliente para que confirme los datos. El usuario podría volver a ingresar los datos si encuentra errores. No supongas ningún dato."""

#En esto resulta pero no siempre
#Hola, me llamo Alexo y soy el asistente de la plataforma Alectrico. Estoy aquí para ayudarte a contactar con un electricista a domicilio en Providencia, Chile.

#Para empezar, necesito algunos datos para llenar una ficha con información sobre ti y el problema que estás experimentando. ¿Podrías proporcionarme, por favor, el siguiente información:

#1. ¿Cuál es tu nombre?
#2. ¿Cuál es tu teléfono de contacto?
#3. ¿En qué comuna te encuentras?
#4. ¿Cuál es la dirección del lugar donde se reporta el problema?
#5. ¿Cuál es tu dirección de correo electrónico?

#Además, tengo tres opciones para que puedas elegir cómo proceder:

#* Puedo sugerirte un electricista que se adapte a tus necesidades.
#* Puedes elegir un electricista de una lista de opciones.
#* Puedes llenar un cuestionario detallado que será enviado a los electricistas interesados.

#¿Cuál de estas opciones prefieres? 
#..................... 

                        presentacion="""Te llamas alexo y eres el asistente de la plataforma alectrico, la cual contacta en Providencia, Chile a las personas con electricistas a domicilio.
En primer lugar debes conseguir una ficha con los siguientes datos:

1. Descripción
2. Nombre
3. Teléfono
4. Comuna
5. Dirección
6. email

Debes preguntar si el cliente quisiera que le sugieran un electricista, o sí prefiere elegirlo de una lista o si prefiere llenar un cuestionario detallado que será envíado a los electricistas interesados. Debes llenar una ficha con los siguientes datos: nombre: Nombre de la persona que recibirá al electricista, comuna: Comuna hacia donde se deba dirigir el electricista, dirección: Dirección del lugar donde se reporta el problema, descripción: Descripción del problema, fono: Teléfono de contacto al que debe llamar el electricista, email: Dirección de correo electrónico para recibir el contrato y cualquier otra documentación. Cuando tengas la ficha completa, debes mostrársela al cliente para que confirme los datos. El usuario podría volver a ingresar los datos si encuentra errores. No supongas ningún dato."""


                        presentacion_2="""Te llamas Alec y eres el asistente de la plataforma alectrico® repair la cual contacta a las personas con electricistas a domicilio. Debes comenzar por llenar una Solicitud de Atención con el dato siguiente:
En primer lugar

1. Presántate profesionalmente.
En segundo lugar:
2. bes comenzar por llenar una Solicitud de Atención con el dato siguiente:
Descripción del problema, consigue dos detalles por lo menos. No sigas si no tienes este dato. 

Por último 

Obtén los restantes parámetros de la función enviar_aviso. Los cuáles son:

1. Nombre
2. Teléfono
3. Comuna
4. Dirección
5. email
Pide al usuario que escriba en el siguiente formato

 <Parametro>: parametro

Cuando tenga la ficha completa, pida confirmación al usuario para enviar el aviso a los electricistas con estos datos. Con ellos se llenerá la solicitud de atención.

Si el usuario ingresa xxx, debes borrar el chat.
"""

                        mensaje_inicial     = json.dumps( { 'role': 'system', 'content': presentacion } )
                        mensaje_colaborador = json.dumps( { 'role': 'user', 'content': descripcion } )
                        try:
                          await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":system",     mensaje_inicial )
                        except:
                           reply = (
                            f"Bah! Se nos agotaron los recursos, vuelva en un día. \n"
                           )
                           await send_reply(env, wa_id,  reply, True ) 
                           return Response( "Hubo un Error con Alexo", status="200")
                         


                        await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":user" , mensaje_colaborador )
                        presentacion =  await env.INDUCCION_ALEXO.get('INDUCCION_ALEXO')

                        dico =  {
                         'max_tokens': 502,
                         'messages': [ { 'role': 'system', 'content': presentacion },
                                       { 'role': 'user',   'content': descripcion }]}

                        result = await env.AI.run(await env.I.get('MODELO'), to_js (dico ) )

                        if result and result.response:
                          mensaje_gerente =  json.dumps( { 'role': 'assistant', 'content': result.response })
                          await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":assistant" , mensaje_gerente )
                          reply = (
                            f"{result.response} \n"
                            "..................... \n "
                            "Escriba *xxx* para terminar \n "
                          )
                          await send_reply(env, wa_id,  reply, True )

                      else : # "Ya hay mensajes iniciales"
                        console.log("Ya hay mensajes iniciales")
                        mensajes = []
                        mensaje_colaborador = json.dumps( { 'role': 'user', 'content': descripcion } )
                        mensajes_anteriores = await env.DIALOGO.list( prefix = f"{ fono }:no_colaborador" )
                        mensajes.append( { 'role': 'user', 'content': descripcion } )

                        for key in mensajes_anteriores.keys.sort():
                           value = await env.DIALOGO.get(key.name)
                           #Ante la ocurrencia de cualquier error retorna
                           try:
                             mensaje_dict = json.loads(value)
                           except:
                             return False
                           role    = mensaje_dict['role']
                           content = mensaje_dict['content']
                           console.log(f"{role}{content}")
                           mensajes.append( mensaje_dict )

                        
                        orden = str( random.randint(1, 10000))
                        console.log(f"Generando orden {orden} en alexo")

                        dico_con_tools =  {
                         'max_tokens': 502,
                         'messages': mensajes,
                         'tools': [ { 'name': 'cuestionario', 'description': 'Enviar Cuestionario',
                    'parameters': { 'type': 'object','properties': {'nombre':  {'type': 'string', "minLength": 1, 'default': nombre, 'description': "Nombre de la persona que llenará el cuestionario." }}}},
                                       {      'name': 'sugerir_electricista', 'description': 'Sugerir Electricista.' },
                                       {      'name': 'enviar_aviso', 'description': 'Llenar Ficha de Atención.', 'parameters': { 'type': 'object',
                                         'properties': {   'orden': {'type': 'string', 'default': orden, 'description': "Número de la orden de servicio" },
                                                          'nombre': {'type': 'string', 'default': nombre, 'minLength': 1, 'description': "Nombre de la persona que recibirá al electricista"},
                                                        'telefono': {'type': 'string', 'default': wa_id, 'minLength': 1, 'description': 'Teléfono de contacto al que debe llamar el electricista.'},
                                                           'email': {'type': 'string', "minLength": 1, 'description': 'Dirección de correo electrónico para recibir el contrato y cualquier otra documentación.'},
                                                       'direccion': {'type': 'string', "minLength": 1, 'description': 'Dirección donde ocurrió el problema.'},
                                                          'comuna': {'type': 'string', 'default': 'Providencia', "minLength": 1, 'description': 'Comuna hacia donde se debe dirigir el electricista'},
                                                     'descripcion': {'type': 'string', 'default': 'Tengo un problema eléctrico', "minLength": 1, 'description': 'Descripción del problema.'}},
                                                        'required': ['nombre', 'telefono', 'direccion', 'comuna', 'descripcion' ]
                                             }
                                         }
                                      ]
                                   }


                        console.log(f"mensajes {mensajes}")
                        #result = await env.AI.run( await env.I.get('MODELO'), to_js(
                        # {
                        #  'max_tokens': 502,
                        #  'messages': mensajes ,} )) 
                        #Sin usar las tools todavía
                        try:
                          result = await env.AI.run(await env.I.get('MODELO'), to_js (dico_con_tools ) )

                        except AttributeError as e:
                          argumento = e.args[0]
                          if argumento == 'AI':
                            await send_aviso(env, env.FONO_JEFE, "Debe ir Dashboard Binding del worker Cotorro y Agregar Worker AI con nombre 'AI'")

                          reply = (
                                        f"Oucurrió un error de Atributo con Alexo \n"
                                        "Intentélo en unas horas \n"
                                        "----------------")

                          await send_reply(env, wa_id, reply, True )
                          return Response( "Hubo un Error con Alexo", status="200")


                        except Exception as e:
                          reply = (
                                        f"Alexo \n"
                                        "Tal vez se quedó sin recursos \n"
                                        "Intentélo en unas horas \n"
                                        "----------------"
                                        )
                          await send_reply(env, wa_id, reply, True )
                          return Response( "Hubo un Error con Alexo", status="200")



                        if result and hasattr( result, 'tool_calls'):
                            console.log(f"Tiene tool_calls")
                            for call in result.tool_calls:
                                match call.name:
                                   case 'listar_electricistas':
                                     console.log('call.name es listar electricistas')
                                     await listar_electricistas(env, fono)
                                   case 'sugerir_electricista':
                                     console.log("call.name es say_visita")
                                     #Manda una foto mía como sugerido y un precio de visita
                                     amount = env.PRECIO_VISITA

                                     buy_order   = str( random.randint(1, 10000))
                                     path_de_pago = f"/transbank?amount={amount}&session_id={wa_id}&buy_order={buy_order}"
                                     try:
                                       await say_pagar_visita( env, wa_id, '\uD83D\uDE01', amount, path_de_pago )
                                       reply = (
                                        f"¿Podría pagar antes la visita? \n"
                                        "Los electricistas profesionales \n"
                                        "prefieren el pago antes \n"
                                        "..................... \n "
                                        "Escriba *xxx* para terminar \n "
                                        )
                                       await send_reply(env, wa_id,  reply, True )

                                     except:
                                       pass
                                   case 'cuestionario':
                                     console.log("call.name llenar_cuestionario")
                                     #Manda un cuestionario que debe ser llenado
                                     await enviar_template_flow_reservar_a_cliente( request, env, wa_id, call.arguments.nombre )

                                     reply = (
                                      f"Se ha envíado un cuestionario \n"
                                      "..................... \n "
                                      "Escriba *xxx* para terminar \n "
                                     )
                                     await send_reply(env, wa_id,  reply, True )


                                   case 'enviar_aviso':
                                     #Avisar a los electricistas
                                     #Los electricistas pagan
                                     console.log("call.name es enviar_aviso")
                                     console.log(f"call orden {call.arguments.orden}")
                                     console.log(f"call nombre {call.arguments.nombre}")
                                     console.log(f"call telefono {call.arguments.telefono}")
                                     console.log(f"call email {call.arguments.email}")
                                     console.log(f"call direccion {call.arguments.direccion}")
                                     console.log(f"call comuna {call.arguments.comuna}")
                                     console.log(f"call descripcion {call.arguments.descripcion}")

                                     reply = (
                                      f"Se intenta enviar aviso a los electricistas \n"
                                      f"{call.arguments.nombre} \n"
                                      "..................... \n "
                                      "Escriba *xxx* para terminar \n "
                                     )
                                     await send_reply(env, wa_id,  reply, True)
                                     if not len( call.arguments.nombre ) > 1:
                                        reply = (
                                        f"Ingrese un nombre \n"
                                        "..................... \n "
                                        "Escriba *xxx* para terminar \n "
                                        )
                                        await send_reply(env, wa_id,  reply, True )


                                     if not len( call.arguments.telefono ) > 1:
                                        reply = (
                                        f"Ingrese un telefono \n"
                                        "..................... \n "
                                        "Escriba *xxx* para terminar \n "
                                        )
                                        await send_reply(env, wa_id,  reply, True )


                                     if not len( call.arguments.email ) > 1:
                                        reply = (
                                        f"Ingrese un email \n"
                                        "..................... \n "
                                        "Escriba *xxx* para terminar \n "
                                        )
                                        await send_reply(env, wa_id,  reply, True )

                                     if not len( call.arguments.direccion ) > 1:
                                        reply = (
                                        f"Ingrese un direccion \n"
                                        "..................... \n "
                                        "Escriba *xxx* para terminar \n "
                                        )
                                        await send_reply(env, wa_id,  reply, True )

                                     if not len( call.arguments.comuna ) > 1:
                                        reply = (
                                        f"Ingrese una comuna \n"
                                        "..................... \n "
                                        "Escriba *xxx* para terminar \n "
                                        )
                                        await send_reply(env, wa_id,  reply, True )
                                     if not len( call.arguments.descripcion ) > 1:
                                        reply = (
                                        f"Ingrese una descripcion \n"
                                        "..................... \n "
                                        "Escriba *xxx* para terminar \n "
                                        )
                                        await send_reply(env, wa_id,  reply, True )



                                     resultado = await enviar_aviso(env, call.arguments.nombre,
                                                                         call.arguments.telefono,
                                                                         call.arguments.email,
                                                                         call.arguments.direccion,
                                                                         call.arguments.comuna,
                                                                         call.arguments.descripcion,
                                                                         call.arguments.orden)
                                     if resultado:
                                       mensaje = f"La orden {call.arguments.orden} ha sido entregada a los colaboradores. Esta es la descripcion {call.arguments.descripcion}."
                                       tool_resultado = json.dumps( { 'role': 'tool', 'content': mensaje  } )
                                       await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":tool" , tool_resultado )
                                       dico =  {
                                       'max_tokens': 502,
                                       'messages': [
                                              { 'role': 'user',   'content': tool_resultado },
                                              { 'role': 'user',   'content': 'xxx'}
                                                   ]}
                                       #Llamo al LLM para que se imponga del resultado 
                                       try:
                                         result = await env.AI.run(await env.I.get('MODELO'), to_js (dico ) )
                                       except Exception as e:
                                          console.log("Hubo un error {e}")
                                          reply = (
                                          f"Hubo un error {e} \n"
                                          "Reintente en unas horas \n"
                                          "..................... \n "
                                          "Escriba *xxx* para terminar \n "
                                          )
                                          await send_reply(env, wa_id,  reply, True )
                                          await xxx( env, wa_id )
                                          return False   
                                      
                                       if result and result.response:
                                        console.log(f"{result.response}")
                                        reply = (
                                        f"{result.response} \n"
                                        "..................... \n "
                                        "Escriba *xxx* para terminar \n "
                                        )
                                        await send_reply(env, wa_id,  reply, True )
                                        
                                        #await env.DIALOGO.put( str(fono) + ":" + "no_colaborador" +  str(datetime.now()) + ":user" , mensaje_colaborador )
                                        #mensaje_gerente =  json.dumps( { 'role': 'assistant', 'content': result.response })
                                        #await env.DIALOGO.put( str(fono) + ":" + "no_colaborador" +  str(datetime.now()) + ":assistant" , mensaje_gerente )
                                        #Cerrando el chat
                                        await xxx( env, wa_id )
                            return Response( "For Calls", status = "200")
                        return Response( "Es tool", status = "200" )
                      return Response( "Es Colaborador", status="200")


#-------------------------------------------------- FIN AI --------------------------------------------------------

#no se usa
async def enviar_template_say_visita_flow_reservar_a_colaborador( request, env, fono):
        #'say_visita' está idéntica en canal colaborador, whatsapp Colaborador
        #'flow_reservar' es el nombre que tiene en whatsapp Cliente
        console.log("En enviar_template say_visita -> flow reserva")
        imagen_url = f"{env.API_URL}/{env.LOGUITO_PATH}"

        bearer, phone_id = await get_bearer_and_phone( env, False)

        uri        = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
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
             "Authorization": f"Bearer {bearer}",
             "content-type": "application/json;charset=UTF-8"
           },
        }
        #--- anota que se envió un cuestionario, porque podría darse como failed
        #--- anota que se envió un cuestionario, porque podría darse como failed
        response = await fetch(uri, to_js(options))
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        result_dict = json.loads( result )
        id = result_dict['messages'][0]['id']
        console.log(f"id {id}")
        try:
          await env.BUY_ORDER.put( id, 'say_visita -> flow reserva', { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION } )
        except:
          pass
        #---------------------------------------------------------------------------------------
        return Response( 'ok', status="200")


#importatnte, envia un formulario
async def enviar_template_flow_reservar_a_cliente( request, env, fono, nombre):
        #'say_visita' está idéntica en canal colaborador, whatsapp Colaborador
        #'flow_reservar' es el nombre que tiene en whatsapp Cliente
        console.log("En enviar_template say_visita -> flow reserva")
        imagen_url = f"{env.API_URL}/{env.LOGUITO_PATH}"
 
        bearer, phone_id = await get_bearer_and_phone( env, True)

        uri        = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
        body = {
          "messaging_product": "whatsapp",
          "to": f"{fono}",
          "type": "template",
          "template": {
            "name": "flow_reservar",
            "language": {
              "code": "es"
          },
          "components": [
           { "type": "body",   "parameters": [ { "type": "text", "text": nombre }]},
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
             "Authorization": f"Bearer {bearer}",
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
          await env.BUY_ORDER.put( id, 'say_visita -> flow reserva', { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION } )
        except:
          pass
        #---------------------------------------------------------------------------------------
        return Response( 'ok', status="200")


#--------------- Funciones llamadas desde LLMs .---------------------
async def enviar_aviso( env, nombre, telefono, email, direccion, comuna, descripcion, orden):
  console.log( "En enviar_aviso")

  reply = (
    "*ENVIANDO..*\n"
    f"orden  {orden} \n"
    f"nombre {nombre}\n"
    f"telefono {telefono}\n"
    f"comuna {comuna}\n"
    f"direccion {direccion}\n"
    f"email {email}\n"
    f"descripcion {descripcion}\n"
  ) 

  await send_reply( env, telefono, reply, True)
  amount = env.PRECIO_VISITA
  console.log("Estoy en enviar_aviso, antes de difundir_a_colaboradores")
  return await difundir_a_colaboradores(env, orden, nombre, (nombre + ' | ' + str(telefono)[0:3] + '.. | ' + descripcion ) , comuna, telefono, email, direccion, amount)
  



async def listar_electricistas( env, wa_id):
  console.log( "En listar_electricistas")

  lista = []

  electricistas = await env.NOMINA.list( prefix = "activo:" )
  for key in electricistas.keys:
         
         token = await env.NOMINA.get( key.name )
         token_dict = json.loads(token)
         nombre  = token_dict['nombre']
         fono    = token_dict['fono']
         lista.append(f"{nombre} {fono}\n")

  reply = (
    "ELECTRICISTAS ACTIVOS*\n"
    f"{lista}\n"
  )

  await send_reply( env, wa_id, reply, True)
  return f"La lista de electricistas se la sido entregada."


#----------------------------- WORKER ENTRYPOINT --------------------
async def on_fetch(request, env):

    url = urlparse(request.url)
    params = parse_qs(url.query)
    method = request.method
    #console.log(f"META_USER_TOKEN {await env.META.get('USER_TOKEN')}")

    console.log(f"Handling request {url.path} with params {params}")
    if url.path == '/testing_flow':
        console.log(f"Params en /testing_flow {params}")
        return success_mostrar_fono(env,  f"Felicitaciones, el flow ha sido probado con éxito.", 9)
  
    elif url.path == '/etherdog.png':
       ruta    = 'etherdog.png'
       archivo = await env.MEDIA.get(ruta)
       return Response(archivo.body, status = "200")

    elif url.path == '/difundir_saldos':
       await difundir_saldos(env) 
       return success_mostrar_fono(env,  f"Saldo Envíando.", 9)
 
    elif url.path == '/enviar_concurso':
       await difundir_concurso(env)
       return success_mostrar_fono(env,  f"Concurso difundido.", 9)

    #---------- FORMULARIO DE JORGITO's MEDICARE ---------
    elif url.path == '/create_from_jorgitos_landing_page.json' and method== 'OPTIONS':
        console.log(f"Params en /create_from_jorgitos_landing_page {params}")

        body = await request.text()
        buy_order    = str( random.randint(1, 10000))

        session_id   = buy_order
        amount       = env.PRECIO_VISITA
        params       = parse_qs( body )

        name         = params['fname']
        fono         = params['phone']
        email        = params['email']
        descripcion  = params['subject']
        comuna       = 'Texas'
        direccion    = '5945 Bellaire Blvd, Ste F, Houston, TX 77081'

        await guardar_pedido( env, buy_order, fono, name, email, direccion, comuna, descripcion,  amount )

        await derivar_jefe(env, name, descripcion, direccion, buy_order, comuna)
        headers =  { "Access-Control-Allow-Origin": "*" }
        return Response( 'ok', status="200", headers=headers )

    #----------  FIN DE ATENCIÓN A JORGITO's MEDICARE -------------------------------
    #---------- FORMULARIO DEL INGENIERO EN LANDING PAGES, NO ESTÁ EN TODAS ---------
    elif url.path == '/create_from_landing_page' and method== 'POST':
        console.log(f"Params en /create_from_landing_page {params}")

        body = await request.text()
        buy_order    = str( random.randint(1, 10000))

        session_id   = buy_order
        amount       = env.PRECIO_VISITA
        params       = parse_qs( body )

        name         = params['data[0][]'][1]
        fono         = params['data[1][]'][1]
        email        = params['data[2][]'][1]
        descripcion  = params['data[3][]'][1]
        comuna       = params['data[4][]'][1]
        direccion    = params['data[5][]'][1]
        #landing_page = params['data[6][]'][1]
        await guardar_pedido( env, buy_order, fono, name, email, direccion, comuna, descripcion,  amount )

        await derivar_jefe(env, name, descripcion, direccion, buy_order, comuna)
        headers =  { "Access-Control-Allow-Origin": "*" }
        return Response( 'ok', status="200", headers=headers )
   #-----------------------------------------------------------------------------------


    elif url.path == "/favicon.ico":
          return Response("")


    #Esto viende del QR de la chaqueta -----------------------------------------------
    #https://www.alectrico.cl/v/uR21SF_P0pnd8rQAMGSfEg/verifica_user
    elif url.path == '/v/uR21SF_P0pnd8rQAMGSfEg/verifica_user':
        await say_jefe(env, f"Hola Jefe, alguien llegó a verifica_user" )
        return Response.redirect( env.ALEC_SEC_URL, 307)
        #return agendar(env, '/v/uR21SF_P0pnd8rQAMGSfEg/verifica_user')
    #-----------------------------------------------------------------------------------

    #entrypoint cuando se llama directamente a www.alectrico.cl
    #--------------------  PRESENTA UN FORMULARIO QUE TERMINA EN AGENDAR ----------
    elif url.path == '/':
        return agendar(env, 'Ingrese los datos para Agendar una Visita a Domicilio')
    #-----------------------------------------------------------------------------------

    #--------------------- EL COLABADORADOR DESEOSO DE ATENDER LLEGA CON EL BUY ORDER -----
    elif url.path == '/atender':
        console.log(f"Params en /atender {params}")
        try:
          buy_order = params['buy_order'][0]
          fono_colaborador = params['fono_colaborador'][0]
        except:
          return mostrar_not_found(env, "Ocurrió un error al procesar los parámetros. Lo sentimos.")

        fono = await get_fono_cliente( env, buy_order)
        fono_str = str(fono)
        if fono:
          fono_cliente = fix_fono( fono )
          #------------------ identificar al colaborador ------

          fono = fix_fono( fono_colaborador )
          pagados = await env.FINANCIERO.list(prefix = f"{fono}:token:pagado:")
          pagados_count = len(pagados.keys)

          console.log(f"Tokens pagados en total {pagados_count} para el fono {fono}")
          for key in pagados.keys:
                 try:
                     token = await env.FINANCIERO.get( key.name )
                     token_dict = json.loads(token)
                     expira_en  = token_dict['token']['expira_en']
                     orden      = token_dict['token']['orden']
                     console.log(f"expira en {expira_en}")
                     if datetime.today() > datetime.fromisoformat( expira_en ):
                       try:
                          token_expirado = f"{fono}:token:pagado:expirado:{orden}"
                          await env.FINANCIERO.put(f"{token_expirado}", token)
                          console.log(f"token marcado como expirado {token_expirado}")
                       except:
                          return mostrar_not_found( env, f"{token} Lo sentimos, hubo un error al guardar en la base de datos. Refresque la página en unos momentos.")
                 except:
                    return mostrar_not_found( env, f"{token} Lo sentimos, hubo un error al leer de la base de datos. Refresque la página en unos momentos.")

          no_expirados = await env.FINANCIERO.list(prefix = f"{fono}:token:pagado:no_expirado")

          console.log(f"Token no expirados en todal  {len( no_expirados.keys)}, uno de los cuales será eliminado")
          #Caso de uso
          #En mi rol de alectrico
          #Dado que quiero un trato justo
          #Debo usar primero los tokens que expiran más temprano
          if len(no_expirados.keys) > 0:
             names = []
             for key in no_expirados.keys:
               console.log(f"key {key.name}")
               names.append( key.name )
             names_sorted = names.sort

             #Este expira más temprano que el resto
             name_key_mas_expirable = names[0]

             console.log(f"name_key_mas_expirable {name_key_mas_expirable}")
             try:
               token = await env.FINANCIERO.get( name_key_mas_expirable )
             except:
               return mostrar_not_found( env, f"Lo sentimos, hubo un error al leer de la base de datos. Refresque la página en unos momentos.")
             try:
                await env.FINANCIERO.delete( name_key_mas_expirable)
                console.log(f"Se ha eliminado el token más expirable {name_key_mas_expirable}")

                try:
                  await env.BUY_ORDER.delete( str(buy_order))
                  return success_mostrar_fono(env,  f"Felicitaciones, ha tomado el pedido  con éxito. Puede llamar ahora al cliente al {fono_cliente}.", fono_cliente)
                except:
                  return mostrar_not_found( env, f"Ya ha pagado, pero la orden {buy_order} sigue vigente. No intente pagar de nuevo esta orden. Avise a alectrico de este error.")
             except:
                return mostrar_not_found( env, f"Lo sentimos, este pedido {buy_order} ya no está vigente.")
          else:
            return mostrar_not_found( env, f"No hay tokens disponibles. Debe comprar más en https://recarga.alectrico.cl ")
        else:
          return mostrar_not_found( env, f"Lo sentimos, este pedido {buy_order} ya no está vigente.")


    #------------------------------------------------------------------------------------------------
    #----------------------------------------- FORMULARIOS WEBS LLAMAN A AGENDAR ---------------------
    #Esos formularios son un poco diferentes a los usuales usan un assets llamado formoide en las
    #landing_pages

       #agendar?nombre=oipoi+upoi&fono=987654321&email=hjhkjh%40lkjlkj.ll&comuna=Providencia&descripcion=lkñ+jñlkj&direccion=o+ṕoiṕoiṕo&latitude=&longitude=&amount=68000
    elif url.path == '/agendar':
        console.log(f"Params en /agendar {params}")
        buy_order   = str( random.randint(1, 10000))
        fono        = params['fono'][0]
        descripcion = params['descripcion'][0]
        amount      = params['amount'][0]
        name        = params['nombre'][0]
        direccion   = params['direccion'][0]
        comuna      = params['comuna'][0]
        email       = params['email'][0]

        #no se envía el cuestionario, porque se vería repetido
        #await enviar_template_say_visita_flow_reserva(request, env, fono )
        await say_jefe( env, f"en agendar {fono} {descripcion}")


        reply   = (
                    f"*buy_order*    { buy_order}     \n"
                    f"*amount*       { amount}        \n"
                    f"*fono*         { fono     }    \n"
                    f"*descripcion*  { descripcion } \n"
                  )

        token_ws, uri = await genera_link_de_pago_tbk( buy_order, amount, env.RETURN_URL, fono, env)
        await guardar_pedido( env, buy_order, fono, name, email, direccion, comuna, descripcion,  amount )
        console.log("Estoy en /agendar, antes de difundir_a_colaboradores")
        await difundir_a_colaboradores(env, buy_order, name, descripcion, comuna, fono, email, direccion, env.PRECIO_TOKEN)
        return mostrar_formulario_de_pago(request, env, buy_order, amount, uri, token_ws)

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

    #--------------------  WEBHOOK AE -----------------------------------------------------
    elif url.path == "/webhook_ae" and method== 'GET':
        if params["hub.mode"] == ['subscribe'] and params['hub.verify_token'][0] == env.VERIFY_TOKEN:
          return Response(params['hub.challenge'][0], status=200)
        else:
          return Response("Error", status=403)

    #elif url.path == "/webhook_ae"  and method== 'POST': # corresponde a la ap ae
    #    request_json = await request.json()
        #console.log( f"request_json {request_json}")


        #Atiende los llamados VoIP de Whatsapp ---
    #    value = request_json.entry[0].changes[0].value


    #    if hasattr(value, 'messages') == True :
    #        console.log("Es un mensaje")

    #        if hasattr(value.messages[0], "type") and value.messages[0] == "request_welcome":
    #           reply = (
    #            "Bienvenido a la plataforma alectrico® repair \n"
    #           )
    #           await send_reply( env, wa_id, reply, False )
    #           return Response( "Procesado", status="200")

        #try:
        # wa_id = request_json.entry[0].changes[0].value.contacts[0].wa_id
        # console.log("En webhook_ae")
        # reply = (
	#  "Bienvenido a la plataforma alectrico® repair \n"
        #)
        # await send_reply( env, wa_id, reply, True )
        #except:
        #  pass
    #     return Response( "Procesado", status="200")

    elif url.path == "/webhook_ai" and method == 'POST':
        return Response( "Procesar con alectrico.ai en otro repo, en otro worker", status = 200)

    #---------------------- WEBHOOK COTORRO ------------------------------------------------
    elif url.path == "/webhook_cotorro" and method== 'GET':
        if params["hub.mode"] == ['subscribe'] and params['hub.verify_token'][0] == env.VERIFY_TOKEN:
          return Response(params['hub.challenge'][0], status=200)
        else:
          return Response("Error", status=403)


    elif ( url.path == "/webhook_cotorro" or url.path == "/webhook_ae") and method == 'POST': 
        console.log("En webhook_cotorro or webhook_ae" )

        request_json = await request.json()

        #console.log( f"request_json {request_json}")

        #Atiende los llamados VoIP de Whatsapp ---
        value = request_json.entry[0].changes[0].value

        #try:
        #  wa_id = request_json.entry[0].changes[0].value.contacts[0].wa_id
        #  reply = (
        #  "Bienvenido a la plataforma  alectrico® exo! \n"
        #  )
        #  await send_reply( env, wa_id, reply, False )
        #except:
        #  pass

        #console.log( f"hasattr messages    {hasattr(value, 'messages')} " )
        #console.log( f"hasattr contacts    {hasattr(value, 'contacts')} " )
        #console.log( f"hasattr statuses    {hasattr(value, 'statuses')} " )
        #console.log( f"hasattr calls       {hasattr(value, 'calls')} " )


        if hasattr( value, 'calls') and hasattr(value, 'contacts') :
                               nombre       = value.contacts[0].profile.name
                               fono_cliente = value.contacts[0].wa_id
                               de           = getattr( value.calls[0], 'from' )
                               to           = value.calls[0].to
                               call_id      = value.calls[0].id
                               event        = value.calls[0].event
                               timestamp    = value.calls[0].timestamp
                               if event == "connect":
                                 sdp_type     = value.calls[0].session.sdp_type
                                 sdp          = value.calls[0].session.sdp
                                 reply = (
                                 "------------------------------ \n\n"
                                 "--- LLAMADO WHATSAPP DE: ----- \n\n"
                                 f"*call_id:*\t{call_id}\n\n"
                                 f"*sdp_type:*\t{sdp_type}\n\n"
                                 f"*sdp:*\t{sdp}\n\n"
                                 f"*event:*\t{event}\n\n"
                                 f"*from:*\t{de}\n\n"
                                 f"*to:*\t{to}\n\n"
                                 "------------------------------ \n\n"
                                 )
                                 console.log(f"reply {reply}")
                                 await send_reply(env, env.FONO_JEFE , reply, False)
                                 #await responder_call( env, call_id, "answer" , sdp , "pre_accept")
                                 await responder_call( env, call_id, "answer" , sdp , "accept")

                               else:
                                 reply = (
                                 "------------------------------ \n\n"
                                 "--- LLAMADO WHATSAPP DE: ----- \n\n"
                                 f"*call_id:*\t{call_id}\n\n"
                                 f"*event:*\t{event}\n\n"
                                 f"*from:*\t{de}\n\n"
                                 f"*to:*\t{to}\n\n"
                                 "------------------------------ \n\n"
                                 )
                                 console.log(f"reply {reply}")
                                 await send_reply(env, env.FONO_JEFE , reply, False)


                               return Response( "Procesado", status="200")


        if hasattr(value, 'messages') == True :

            console.log("Es un mensaje")

            #Cuando alguien escribe un texto en los canales de publico suscritos
            #Se recibe aquí
            #No funciona, pero alguna vez funcionó en otros lenguajes de este software
            if hasattr(value.messages[0], "type") and value.messages[0] == "request_welcome":
               reply = (
                "Bienvenido a la plataforma alectrico® exo! \n"
               )
               await send_reply( env, wa_id, reply, False )
               return Response( "Procesado", status="200")


            elif hasattr(value.messages[0], 'button') == True :
               console.log("Es button")
               descripcion = value.messages[0].button.payload
               wa_id       = request_json.entry[0].changes[0].value.contacts[0].wa_id
               colaborador_json = await env.NOMINA.get( "activo:" + str( fix_fono( wa_id) ))
               colaborador = json.loads( colaborador_json )
               nombre_colaborador = colaborador['nombre']

               if await es_colaborador(env, wa_id):
                  console.log(f"{wa_id} es colaborador")
                  buy_order   = str( random.randint(1, 10000))
                  
                  match descripcion: 
                    case "Recargar":
                      console.log("Es Recargar")
                      path_de_pago = f"/recargar?fono={fix_fono(wa_id)}&cantidad=1&nombre=&email=&comuna=Providencia&descripcion=&direccion=&amount={env.PRECIO_TOKEN}"
                      await say_link_de_recarga( env, wa_id, '\uD83D\uDE01',  env.PRECIO_TOKEN, path_de_pago )
                      return Response( "No Procesado", status="200")

                    case "Tomar":
                       console.log("Es Tomar")
                       id = value.messages[0].context.id
                       if id:
                          console.log(f"id {id}")
                          buy_order = await env.DICT.get(id)
                          if buy_order:
                            console.log(f"buy_order {buy_order}")

                            nombre_cliente = await get_nombre_cliente( env, buy_order)
                            fono_cliente   = await get_fono_cliente( env, buy_order)
                            console.log(f"fono_cliente {fono_cliente}")

                            descripcion    = await get_descripcion_cliente( env, buy_order)
                            comuna         = await get_comuna_cliente( env, buy_order)

                            #NOTA: tomar_tokn borrará el pedido dadopor buy_order
                            #no se puede usar nada de los cuatros gets de arriba
                            await tomar_token(env, wa_id, buy_order )
                            if fono_cliente:
                               console.log(f"fono_cliente {fono_cliente}")
                               #reply = (
                               #"------------------------------ \n\n"
                               #f"*Orden*:\t{buy_order}\n\n"
                               #f"*Cliente Nombre:*\t{nombre_cliente}\n\n"

                               #f"*Fono de su Cliente:*\t{fono_cliente}\n\n"
                               #"------------------------------ \n\n"
                               #)
                               #console.log(f"reply {reply}")
                               #await send_reply(env, wa_id, reply, False)


                               reply = (
                               "------------------------------ \n\n"
                               f"*Orden*:\t{buy_order}\n\n"
                               f"*Fono de su Electricista:*\t{wa_id}\n\n"
                               "------------------------------ \n\n"
                               )
                               console.log(f"reply {reply}")
                               await send_reply(env, fono_cliente, reply, True)

                               await say_confirmacion_de_caso( env, wa_id, nombre_colaborador, nombre_cliente, fono_cliente, descripcion, comuna )


                            else:
                               console.log("No se pudo obtener fono de cliente")
                       else:
                            console.log(f"id {id} no tiene buy_order")
               return Response( "No Procesado", status="200")





            if hasattr(value.messages[0], 'text') == True:

               console.log("Es text")
               console.log(f"body {value.messages[0].text.body}")

               descripcion = value.messages[0].text.body
               id          = value.messages[0].id
               wa_id       = request_json.entry[0].changes[0].value.contacts[0].wa_id
               fono        = str( fix_fono ( wa_id ))
               nombre      = request_json.entry[0].changes[0].value.contacts[0].profile.name

               match descripcion:

                    case "/comprar_tokens":
                      path_de_pago = f"/recargar?fono={fix_fono(wa_id)}&cantidad=1&amount={env.PRECIO_TOKEN}"
                      await say_link_de_recarga( env, wa_id, '\uD83D\uDE01',  env.PRECIO_TOKEN, path_de_pago )
                      return Response( "Compra de Tokens", status="200")
                    case "/activar":
                      await activar( env, wa_id )
                      return Response( "Ahora está activo Colaborador", status="200")

                    case "/desactivar":
                      await desactivar( env, wa_id )
                      return Response( "Ahora está inactivo el Colaborador", status="200")

                    case "/desuscribir":
                      await desactivar( env, wa_id )
                      return Response( "El Colaborador ha dejado de estar suscrito", status="200")

                    case "/suscribir":
                      await suscribir( env, wa_id, nombre)
                      return Response( "El Colaborador ahora está está suscrito", status="200")

                    case "xxx":
                          console.log("Procesando xxx")
                          await xxx( env, wa_id)
                          return Response("xxx", status = "200")

                    case "Xxx":
                          console.log("Procesando Xxx")
                          await xxx( env, wa_id)
                          return Response("xxx", status = "200")


               

               #alexo solo para los que no son colaboradores
               if not await es_colaborador(env, wa_id):
                   console.log(f"{wa_id} No es colaborador")
                   await alexo( env, request, wa_id, descripcion, nombre)
                   return Response( "Ud. No es Colaborador", status="200" )

               #alambrito solo para los que sean colaboradores
               else:
                   console.log(f"{wa_id} es colaborador")
                   #   await canal_colaborador_ai(env, wa_id, descripcion)
                   saldo = int( await get_saldo( env, wa_id) )
                   console.log(f"saldo {saldo}")
                   #reply=( f"Su saldo Actual en tokens que puede usar es de: \n"
                   #        f" {saldo}")
                   #await send_reply( env, wa_id, reply, False)

                   if saldo > 0:
                     buy_order = str( random.randint(1, 10000))
                     #await tomar_token(env, wa_id, buy_order )
                     try:
                       await alambrito(env, wa_id, descripcion)
                     except:
                       reply=( f"Ocurrió un error con Alam Brito \n")
                       await send_reply( env, wa_id, reply, False)                       

                   else: 
                     try:
                       await canal_colaborador_ai(env, wa_id, descripcion)
                     except:
                       reply=( f"Oucurrió un error con Alam Brito  \n")
                       await send_reply( env, wa_id, reply, False)                       
               return Response( "Procesado como text", status="200" )




            #----------------------- LLAMANDO A FUNCIONES AI -----------------------------------   
            #Cuando el usuario responda cuestionarios
            #Llega aquí
            
            #Los proceso
            #Con varios calificadores
            #Cada uno busca su palabra clave 
            if hasattr(value.messages[0], 'interactive') == True :
               console.log("Es interactive")
               if hasattr(value.messages[0].interactive, 'nfm_reply') == True :
                   console.log("Es nfm_reply")
                   if hasattr(value.messages[0].interactive.nfm_reply, 'response_json') == True :
                       console.log("Tiene response_json")
                       #no puedo difundir_a_colaboradores aquí, lo hago desde dentro del flow_reply_processor
                       try:
                         response_json = request_json.entry[0].changes[0].value.messages[0].interactive.nfm_reply.response_json
                         flow_data = json.loads(response_json)

                         if flow_data['screen_0_recintos']:
                             await concurso_calificador( request_json, env)
                         elif flow_data['sintomas']:
                             await flow_reply_processor( request_json, env)
                       except:
                         pass
                       return Response( "Procesado", status="200")


            console.log(f"Es un mensaje y nada más: {value}")
            return Response( "no procesado", status="200")



        elif hasattr(value, 'statuses') == True :
            console.log("Es un statuses")
            status = value.statuses[0].status
            id     = value.statuses[0].id
            wa_id        = request_json.entry[0].changes[0].value.statuses[0].recipient_id
            resultado = await env.BUY_ORDER.get(str(id) )

            #onsole.log(status)
            #Guardando el status para futura referencia
            await save_status(env, id, status, wa_id )

            #ya no estoy vigilando failed,
            #Solo envío el cuestiari y el link de pago al comienzo
            match status:
                 case 'failed':
                    console.log(f"{value.statuses[0].errors[0].title}")
                    #Busco el objeto que ha fallado
                    #Compruebo que haya sido un fallo al enviar el template say_visita
                    #Verifico que el error sea de Message undeliverable 
                    #Eso cubre a los fonos inexisentes, redes que no funcionan con waba
                    #Y versiones de androide menores a la exigida para esa característica de cuestionarios
                     
                    if resultado == 'say_visita -> flow reserva' and value.statuses[0].errors[0].title == 'Message undeliverable':
                           #Intento eliminar el registro de este envío fallido
                           #De esa forma evito que se vuelva a reaccionar sobre lo mismo, más adelante
                           #Se usa try porque el kv_name está limitado a 1000 operaciones diarias
                           #Si falla algo aquí no podré otorgar Response 200
                           #Esto ocurre para un cliente al que le envíe el formulario para que especifique la visita
                           await save_status(env, id, 'failed -> Message undeliverable', wa_id )

                           wa_id        = request_json.entry[0].changes[0].value.statuses[0].recipient_id
                           buy_order    = str( random.randint(1, 10000))
                           direccion    = 'no indica'
                           comuna       = 'no indica'
                           descripcion  = 'no indica'
                           email        = 'user@alectrico.cl'
                           name         = 'no indica'
                           amount       = env.PRECIO_VISITA

                           reply = (
                             "Hubo un error, el cuestionario no es compatible con su celular.  \n"
                             "Solo pida lo que necesita e intentaremos avisar a los electricistas. \n"
                           )
                           await send_reply(env, wa_id, reply, True)
                           fono = fix_fono( wa_id )
                           try:
                             mensaje_reply= json.dumps( { 'role': 'tool', 'content': "Error: El cuestionario no pudo ser entregado porque no es compatible con su celular." })
                             await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":tool",     mensaje_reply )

                             mensaje_reply= json.dumps( { 'role': 'system', 'content': "No ofrezcas enviar cuestionario porque está con problemas con este usuario." })
                             await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":system",     mensaje_reply )

                           except Exception as e:
                             console.log(f"Ocurrió un error al intentar  interactuar con DIALOGO: {e}")
                             pass

                           #try:
                           #  await guardar_pedido( env, buy_order, wa_id, name, email, direccion, comuna, descripcion, amount)
                           #except:
                           #  pass

                           #intentaré enviar un mensaje, pero eso funciona solo en le ventana de anteción
                           #link_de_pago = f"{env.API_URL}/transbank?amount={env.PRECIO_PROCESO}&session_id={wa_id}&buy_order={buy_order}"
                           #msg = (f"Por favor pague la visita siguiendo el link:\n"
                           #f"link_de_pago: {link_de_pago} {resultado}\n\n")
                           #try:
                           #  await send_msg(env, wa_id, msg, True)
                           # except:
                           #  pass

                           #envío este que debiera funcionar siempre, pero a veces no llega
                           #path_de_pago = f"/transbank?amount={amount}&session_id={wa_id}&buy_order={buy_order}"
                           #try:
                           #  await say_pagar_visita( env, wa_id, '\uD83D\uDE01', amount, path_de_pago )
                           #except:
                           #  pass

                      #Los envíos del concurso, pueden ser rechazados por los colaboradores y se devuelven como failed
                    if resultado == 'say_visita -> flow test_TDA_1' and value.statuses[0].errors[0].title == 'Message undeliverable':
                           #Marco el status como failed
                           await save_status(env, id, 'failed -> Message undeliverable', wa_id )

                    if resultado == 'say_visita -> flow test_TDA_1' and value.statuses[0].errors[0].title == 'This message was not delivered to maintain healthy ecosystem engagement.':
                           await save_status(env, id, 'failed -> This message was not delivered to maintain healthy ecosystem engagement', wa_id )




            return Response( "ok", status="200")


    #----------------------------------------------------------------------------------------

    #-------------------- APOYO PARA LAS LANDING PAGES  EN ---------------------------------

    elif url.path.startswith('/fonos.json'):
        console.log("En fonos.json")
        return fonos(env)
    #-------------------------------------------------------------------------------------

    else:     
      console.log("No se ha identificado")
      return mostrar_not_found(env, "Bah! Ocurrió un Error")
#----------------------------FIN llegada de requests --------------------------


#.......................... MENU PRINCIPAL -----------------------------------
#-----------------------------------------------------------------------------
#@app.route("/webhook", methods=["GET"])
#Hay que hacerlo nuevamente. Se me borró el que usé al comienzo
def webhook_get(request, env, params):
    console.log("En webhook_get")
    if params["hub.mode"] == ['subscribe'] and params['hub.verify_token'] == env.VERIFY_TOKEN:
        return Response(params['hub.challenge'][0], status=200)
    else:
        return Response("Error", status=403)




async def anotar_tokens_pagados_promocionales( env, buy_order, fono, cantidad ):
    fono = fix_fono( fono )
    now = datetime.now()
    fecha_en_el_vencimiento = now + timedelta(days = int( await env.TOKEN_VENCIMIENTO.get()))
    for orden in range(1, cantidad + 1 ):
      orden = str( random.randint(1, 10000))
      pedido = { 'token': {'orden': orden, 'expira_en': str(fecha_en_el_vencimiento), 'buy_order': buy_order, 'fono': fono, "amount": 0, "acuñado_en": json.dumps( date.today().isoformat()) }}
      await env.FINANCIERO.put( f"{fono}:token:pagado:no_expirado:promocional:{orden}", json.dumps(pedido), { 'expirationTtl': await env.TOKEN_VENCIMIENTO.get() })
    return


          #----------------------------- FUNCIONES ------------------------------------------------------
#marca como expirados a los tokens que corresponda
#solo afecta a los tokens del fono proporcionado
async def tomar_token(env, fono, buy_order ):
          console.log("En tomar token")
          buy_order_de_pedido_de_token   = str( random.randint(1, 10000))
          await anotar_tokens_pagados_promocionales( env, buy_order_de_pedido_de_token, fono, 5 )

          fono = fix_fono( fono )
          try:
            pagados = await env.FINANCIERO.list(prefix = f"{fono}:token:pagado:")
            if pagados:
              pagados_count = len(pagados.keys)
              console.log(f"Tokens pagados en total {pagados_count} para el fono {fono}")
            else:
              return false
          except Exception as e: 
              print(e)
              console.log("Ocurrió un error al leer tokens")
              return false

          for key in pagados.keys:
                 try:
                     token = await env.FINANCIERO.get( key.name )
                     token_dict = json.loads(token)
                     expira_en  = token_dict['token']['expira_en']
                     orden      = token_dict['token']['orden']
                     #onsole.log(f"expira en {expira_en}")
                     if datetime.today() > datetime.fromisoformat( expira_en ):
                       try:
                          token_expirado = f"{fono}:token:pagado:expirado:{orden}"
                          await env.FINANCIERO.put(f"{token_expirado}", token)
                          #console.log(f"token marcado como expirado {token_expirado}")
                       except:
                          return False
                 except Exception as e:
                    print( e )
                    return False

          no_expirados = await env.FINANCIERO.list(prefix = f"{fono}:token:pagado:no_expirado")
          console.log(f"Token no expirados en total  {len( no_expirados.keys)}, uno de los cuales será eliminado")
          if len(no_expirados.keys) > 0:
             names = []
             for key in no_expirados.keys:
               #onsole.log(f"key {key.name}")
               names.append( key.name )
             names_sorted = names.sort
             name_key_mas_expirable = names[0]
             #console.log(f"name_key_mas_expirable {name_key_mas_expirable}")
             token = await env.FINANCIERO.get( name_key_mas_expirable )
             await env.FINANCIERO.delete( name_key_mas_expirable)
             console.log(f"Se ha eliminado el token más expirable {name_key_mas_expirable}")
             await env.BUY_ORDER.delete( str(buy_order))
             return True

          return None


async def get_fono_cliente(env, buy_order):
    console.log("En get_fono_cliente")
    console.log(f"buy_order {buy_order}")
    pedido_json = await env.BUY_ORDER.get(str(buy_order))
    if pedido_json:
      pedido = json.loads(pedido_json)
      console.log(f"pedido {pedido}")
      return pedido['pedido']['fono']
    else:
      return None

async def get_nombre_cliente(env, buy_order):
    console.log("En get_nombre_cliente")
    console.log(f"buy_order {buy_order}")
    pedido_json = await env.BUY_ORDER.get(str(buy_order))
    if pedido_json:
      pedido = json.loads(pedido_json)
      console.log(f"pedido {pedido}")
      return pedido['pedido']['name']
    else:
      return None


async def get_descripcion_cliente(env, buy_order):
    console.log("En get_descripcion_cliente")
    console.log(f"buy_order {buy_order}")
    pedido_json = await env.BUY_ORDER.get(str(buy_order))
    if pedido_json:
      pedido = json.loads(pedido_json)
      console.log(f"pedido {pedido}")
      return pedido['pedido']['descripcion']
    else:
      return None

async def get_comuna_cliente(env, buy_order):
    console.log("En get_comuna_cliente")
    console.log(f"buy_order {buy_order}")
    pedido_json = await env.BUY_ORDER.get(str(buy_order))
    if pedido_json:
      pedido = json.loads(pedido_json)
      console.log(f"pedido {pedido}")
      return pedido['pedido']['comuna']
    else:
      return None

async def pedido_exists(env, buy_order):
    console.log("En pedido_exist")
    console.log(f"buy_order {buy_order}")
    pedido_json = await env.BUY_ORDER.get(str(buy_order))
    if pedido_json:
      return True
    else:
      return False






async def save_text_message( env, id, fono, buy_order, descripcion, amount ):
    await env.BUY_ORDER.put( str(buy_order), json.dumps( {"pedido": { "email": "user@alectrico.cl", "fono": fono, 'buy_order': buy_order, 'descripcion': descripcion, 'amount': amount }}), { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION } )
    return


#Guardar status failed
async def save_status( env, id, status, fono) :
    #onsole.log(f"Guardando status {id} {status}")
    #match status:
     #ase'failed':
    await env.STATUS.put( str(fono)+':'+ status + ":" + str(id), status, { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION } )
    return



async def get_fono_cliente(env, buy_order):
    console.log("En get_fono_cliente")
    console.log(f"buy_order {buy_order}")
    pedido_json = await env.BUY_ORDER.get(str(buy_order))
    if pedido_json:
      pedido = json.loads(pedido_json)
      console.log(f"pedido {pedido}")
      return pedido['pedido']['fono']
    else:
      return None



async def guardar_pedido( env, buy_order, fono, name, email, direccion, comuna, descripcion, amount):
    console.log(f"En guardar pedido, buy_order {buy_order}")
    pedido = { 'pedido': {'fono': fono, "name": name, "email": email, "direccion":direccion, "comuna":comuna, "descripcion":descripcion, "amount": amount }}
    if not await pedido_exists( env, buy_order):
      console.log("El pedido no existe")
      await env.BUY_ORDER.put( buy_order, json.dumps(pedido), { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION })
      return True
    else:
      console.log("El pedido existe")
      return False
  

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
   return await send_reply(env, wa_id, reply, True)



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




#Se prepara y luego envía un botón de pago 
#Al que llenó el cuestionario
async def button_reply_processor(request_json, env):
        console.log("En button_reply_processor")
        console.log( f"request_json {request_json}")
        value = request_json.entry[0].changes[0].value.contacts[0]
        console.log(f"value {value}")
        wa_id = request_json.entry[0].changes[0].value.contacts[0].wa_id
        console.log(f"wa_id: {wa_id}")
        response_json = request_json.entry[0].changes[0].value.messages[0].interactive.button_reply.response_json

        console.log(f"response_json {response_json}")

        button_data = json.loads(response_json)

        if 'id' in button_data:
          console.log("Fue econtrado id")
        if 'title' in button_data:
          console.log("Fue encontrado title")

        precio_recarga = env.PRECIO_TOKEN
        console.log(f"precio_recarga {precio_recarga}")
        console.log(f"GO_TBK_URL {env.GO_TBK_URL}")
        console.log(f"buy_order {buy_order}")
        link_de_pago_tbk_url = env.GO_TBK_URL+"/?buy_order="+ str(buy_order) +"&amount="+ str(precio_recarga) + "&session_id=" + str(wa_id)

        reply = (
            "------------------------------ \n\n"
            f"*Orden*:\t{buy_order}\n\n"
            "Por favor siga el link para recargar un token, en Transbank.\n"
            f"*Link_de_pago:*\t{link_de_pago_tbk_url}\n\n"
            "------------------------------ \n\n"
        )
        console.log(f"reply {reply}")
        await send_reply(env, wa_id, reply, True)

async def concurso_calificador( request_json, env):
        console.log("En concurso_clasificador")
        console.log( f"request_json {request_json}")
        value = request_json.entry[0].changes[0].value.contacts[0]
        console.log(f"value {value}")
        wa_id = request_json.entry[0].changes[0].value.contacts[0].wa_id
        console.log(f"wa_id: {wa_id}")
        #enviar saldo antes
        response_json = request_json.entry[0].changes[0].value.messages[0].interactive.nfm_reply.response_json

        console.log(f"response_json {response_json}")


        #---- procesando los campos
        flow_data = json.loads(response_json)

        recinto_1=''
        recinto_2=''
        recinto_3=''
        recinto_4=''
        recinto_5=''
        recinto_6=''
        recinto_7=''

        console.log(f"flow_data {flow_data}")
        if 'screen_0_recintos' in flow_data:
            sintomas = flow_data['screen_0_recintos']
            if '0_Baños' in sintomas:
                recinto_1 = 'Baños'
                console.log("Baños")
            if "1_Cocinas" in sintomas:
                recinto_2 = 'Cocinas'
                console.log("Cocinas")
            if "2_Salas" in sintomas:
                recinto_3 = 'Salas'
                console.log("Salas")
            if "3_Dormitorios" in sintomas:
                recinto_4 = 'Dormitorios'
                console.log("Dormitorios")
            if "4_Lavaderos" in sintomas:
                recinto_5 = 'Lavaderos'
                console.log("Lavaderos")
            if "5_Closets" in sintomas:
                recinto_6 = 'Closets'
                console.log( "Closets" )
            if "6_Despensas" in sintomas:
                recinto_7 = 'Despensas'
                console.log("Despensas")
            if (recinto_2 and recinto_3) and  not (recinto_1 or recinto_4 or recinto_5 or recinto_6 or recinto_7):
              respuesta = "Su respuesta es correcta! Le hemos regalado un token."
              buy_order  = str( random.randint(1, 10000))
              await anotar_tokens_pagados_promocionales(env, buy_order ,wa_id, 1)

            else:
              respuesta = "Su respuesta es incorrecta!"
        reply = (
            f"Gracias por llenar el cuestionario. Estas son las respuestas que hemos guardado:\n\n"
            f"*Recintos*\n\n"
            f"{recinto_1}\n"
            f"{recinto_2}\n"
            f"{recinto_3}\n"
            f"{recinto_4}\n"
            f"{recinto_5}\n"
            f"{recinto_6}\n"
            f"{recinto_7}\n"
            f"{respuesta}\n"
            "------------------------------ \n\n"
        )
        console.log(f"reply {reply}")
        await send_reply(env, wa_id, reply, True)
        await enviar_saldo( env, wa_id )

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


        sintoma_1=''
        sintoma_2=''
        sintoma_3=''
        sintoma_4=''
        sintoma_5=''
        sintoma_6=''

        console.log(f"flow_data {flow_data}")
        if 'sintomas' in flow_data:

            sintoma_id = flow_data['sintomas']

            console.log(f"sintoma_id {sintoma_id}")

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
            "Transbank captura el total pero UD. solo paga cuotas mensuales.\n\n"
            f"*Link_de_pago:*\t{link_de_pago_tbk_url}\n\n"
            "------------------------------ \n\n"
        )
        console.log(f"reply {reply}")
        await send_reply(env, wa_id, reply, True)


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

        precio_visita = env.PRECIO_VISITA
        console.log(f"precio_visita {precio_visita}")
        console.log(f"GO_TBK_URL {env.GO_TBK_URL}")
        console.log(f"buy_order {buy_order}")
        link_de_pago_tbk_url = env.GO_TBK_URL+"/?buy_order="+ str(buy_order) +"&amount="+ str(precio_visita) + "&session_id=" + str(wa_id)

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
            "Transbank captura el total pero UD. solo paga cuotas mensuales.\n\n"
            f"*Link_de_pago:*\t{link_de_pago_tbk_url}\n\n"
            "------------------------------ \n\n"
        )
        console.log(f"reply {reply}")
        await send_reply(env, wa_id, reply, True)

        #envío el path de pago de nuevo con un perrito
        #path_de_pago = f"/transbank/?buy_order="+ str(buy_order) +"&amount="+ str(precio_visita) + "&session_id=" + str(wa_id)
        #wait say_link_de_pago( env, wa_id, '\uD83D\uDE01', precio_visita, path_de_pago )
        #await say_pagar_visita( env, wa_id, '\uD83D\uDE01', str(precio_visita), path_de_pago )
        #await difundir_a_colaboradores(env, buy_order, nombre, descripcion, comuna, fono, email, direccion, env.PRECIO_TOKEN)



#este aviso podría mejorarse , pero como es una comuniación interna lo he dejado así
async def say_jefe(env, descripcion):
        pass


async def say_instrucciones( env, wa_id, nombre, saldo, instruccion_1, instruccion_2, instruccion_3 ):
        console.log("En say_instrucciones")
        console.log(f"wa_id {wa_id}")
        imagen_url = f"{env.API_URL}/{env.FIRST_TAKEME_IMAGE_PATH}"

        body = { "messaging_product" :  "whatsapp",
                "to"                   :  wa_id,
                "type"                 :  "template",
                "template"             : { "name" : "say_instrucciones", "language" : { "code" : "es" },
                    "components"           : [ 
              { "type" :   "body",    "parameters" : [
              { "type"             :   "text", "text" : nombre       } ,
              { "type"             :   "text", "text" : saldo        } ,
              { "type"             :   "text", "text" : instruccion_1},
              { "type"             :   "text", "text" : instruccion_2},
              { "type"             :   "text", "text" : instruccion_3}
            ] } ] }}

        bearer, phone_id = await get_bearer_and_phone( env, False)
        uri     = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {bearer}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return





#este aviso podría mejorarse , pero como es una comuniación interna lo he dejado as, buy_orderí
async def derivar_jefe(env, nombre_cliente, descripcion, direccion, buy_order, comuna):
        return await say_atender(env, str(env.FONO_JEFE), str(env.FONO_JEFE), 'JEFE', direccion, comuna, buy_order)



async def say_confirmacion_de_caso( env, wa_id, nombre, nombre_cliente, fono_cliente, descripcion, comuna ):
        console.log("En say_confirmacion_de_casor")
        console.log(f"wa_id {wa_id}")
        console.log( f"descripcion  {descripcion}")

        bearer, phone_id = await get_bearer_and_phone( env, False)

        body = { "messaging_product" :  "whatsapp",
                "to"                   :  wa_id,
                "type"                 :  "template",
                "template"             : { "name" : "confirmacion_de_caso", "language" : { "code" : "es" },
                    "components"           : [  { "type" :   "body",
                        "parameters" : [
              { "type"             :   "text", "text" : nombre    } ,
              { "type"             :   "text", "text" : descripcion } ,
              { "type"             :   "text", "text" : comuna    },
              { "type"             :   "text", "text" : nombre_cliente } ,
              { "type"             :   "text", "text" : fono_cliente    }
            ] } ] }}

        uri     = f"https://graph.facebook.com/v23.0/{phone_id}/messages"

        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {bearer}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return



async def say_tomar( env, wa_id, nombre, descripcion, comuna, buy_order ):
        console.log("En say_tomar")
        console.log(f"wa_id {wa_id}")
        console.log( f"descripcion  {descripcion}")

        bearer, phone_id = await get_bearer_and_phone( env, False)
        
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

        uri     = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {bearer}"
        }
        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {await env.META.get('USER_TOKEN')}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        result_dict = json.loads( result )
        id = result_dict['messages'][0]['id']
        console.log(f"id {id}") 
        try:
          await env.DICT.put( id, buy_order, { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION } )
        except:
          pass

        return



#Obtiene el saldo en tokens de un colaborador
#presupone que los algoritmos de anotar y tomar tokens
#mantinen bien el regenv, stro de tokens
#anotando pagado:env, o_expirado
async def get_saldo( env, wa_id):
            console.log("En get_saldo")
            fono = fix_fono( wa_id )
            pagados = await env.FINANCIERO.list(prefix = f"{fono}:token:pagado:")
            if len(pagados.keys) > 0:
              console.log("Tiene tokens pagados")
            else: 
              console.log("No tiene tokens pagados")
              return 0

            for key in pagados.keys:
                     token = await env.FINANCIERO.get( key.name )
                     token_dict = json.loads(token)
                     expira_en  = token_dict['token']['expira_en']
                     orden      = token_dict['token']['orden']
                     if datetime.today() > datetime.fromisoformat( expira_en ):
                          token_expirado = f"{fono}:token:pagado:expirado:{orden}"
                          await env.FINANCIERO.put(f"{token_expirado}", token)

            tokens_validos = await env.FINANCIERO.list(prefix = f"{fono}:token:pagado:no_expirado" )
            for token in tokens_validos.keys:
               pass
               #console.log(f"token {token.name}")
            return len( tokens_validos.keys )


async def es_colaborador( env, wa_id):
          fono = fix_fono( wa_id )
          colaboradores = await env.NOMINA.list(prefix = "activo:")
          console.log(f"keys {colaboradores.keys}")
          keys = [key_info.name for key_info in colaboradores.keys]
          console.log(f"keys {keys}")

          if "activo:" + str(fix_fono( wa_id)) in keys:
            console.log(f"{wa_id} es de un colaborador") 
            return True
          else:
             console.log(f"{wa_id} no es de un colaborador")
             return False

def fix_fono( fono ):
          #console.log("En fix_fono")
          fono_str = str(fono)
          # console.log(f"fono_str{fono_str}")
          if '56' in fono_str[0:2]:
             fono = fono_str.replace('56','',1)
             #  console.log(f"fono {fono}")
          return int(fono)

async def difundir_concurso(env):
          console.log("En difundir_concurso")
          colaboradores = await env.NOMINA.list(prefix = "activo:")
          if len(colaboradores.keys) > 0:
             console.log("Hay colaboradores registrados")
             for key in colaboradores.keys:
               wa_id = key.name
               colaborador_json = await env.NOMINA.get( key.name )
               colaborador = json.loads( colaborador_json )
               nombre = colaborador['nombre']
               fono   = colaborador['fono']
               await enviar_concurso( env, fix_fono( fono), nombre )


          
#Difundi los saldos e instrucciones a los colaboradores
async def difundir_saldos(env):
          instruccion_1="*Tomar:* Presione Tomar para conocer el fono del cliente. Esto funciona internamente y no necesita acceso a datos."
          instruccion_2= "*Recargar:* Presione Recargar para comprar un token."
          instruccion_3= "*recarga.alectrico.cl:* Visite https://recarga.alectrico.cl para comprar más de un token."

          console.log("En difundir_saldos")
          console.log("En try")
          colaboradores = await env.NOMINA.list(prefix = "activo:")
          if len(colaboradores.keys) > 0:
             console.log("Hay colaboradores registrados activos")
             for key in colaboradores.keys:
                 wa_id = key.name
                 colaborador_json = await env.NOMINA.get( key.name )
                 colaborador = json.loads( colaborador_json )
                 fono   = colaborador['fono']
                 wa_id  = fono
                 console.log(f"fono {fono}")
                 saldo = await get_saldo( env, fono)
                 console.log(f"saldo {saldo}")
                 nombre = colaborador['nombre']
                 console.log(f"nombre {nombre}")
                 await say_instrucciones( env, wa_id, nombre, saldo, instruccion_1, instruccion_2, instruccion_3 )

#Envia saldo a los colaboradores o al Cliente
async def enviar_saldo(env, wa_id, cliente= False):
        console.log("En enviar saldo")
        colaborador_json = await env.NOMINA.get( "activo:" + str( fix_fono( wa_id)) )
        colaborador = json.loads( colaborador_json )
        saldo = await get_saldo( env, wa_id)
        console.log(f"{saldo}")
        nombre = colaborador['nombre']
        console.log(f"{nombre}")
        reply   = (
                    f"*Su saldo:    \n"
                    f"*Tokens*  { saldo}        \n"
                    f"Nota: El saldo demorará un poco en actualizarse si se ha agregado un token recientemente. \n"
                  )
        console.log(f"replay")
        await send_reply( env, wa_id, reply, cliente)
        return


#Difundi un peido a los colaboradores
async def difundir_a_colaboradores(env, buy_order, name, descripcion, comuna, fono, email, direccion, amount):
        console.log("En difundir a colaboradores")
        token_ws, uri = await genera_link_de_pago_tbk( buy_order, amount, env.RETURN_URL, email, env)
        if await guardar_pedido(env, buy_order, fono, name, email, direccion, comuna, descripcion,  amount ):
          try:
            console.log("En try")
            colaboradores = await env.NOMINA.list( prefix = "activo:" )
            console.log("Después de list")
          except Exception as e:
            await send_aviso(env, env.FONO_JEFE, f"Error en difundir_a_colaboradores, NOMINA.list {e}")
            return
       
          if len(colaboradores.keys) > 0:
            console.log("Hay colaboradores registrados")
            for key in colaboradores.keys:
              console.log(f"{key.name}")
              try:
                colaborador_json = await env.NOMINA.get( key.name )
                colaborador = json.loads( colaborador_json )
                wa_id       = colaborador['fono']
                #taker_fono  = key.name
                taker_fono  = wa_id
                #NOTA: Se envía a wa_id pero el que cobra es taker_fono
                #De esta forma puedo probar cómo funciona
                #Cambiando en env.NOMINA el record {"fono": wa_id}
                #En production ambos serán iguales
                await say_atender(env, wa_id, taker_fono, colaborador['nombre'], descripcion, comuna, buy_order)
              except Exception as e:
                await send_aviso(env, env.FONO_JEFE, f"Error en say_atender {e}")
                return
          return True
        else:
          console.log("No se pudo guardar pedido, difundir a colaboradores está cancelado")
          return False
        return

async def responder_call( env, call_id, sdp_type, sdp, action):
        console.log("En responder_call")
        console.log(f"call_id {call_id}")
        console.log(f"sdp_type  {sdp_type}")
        body = {  "messaging_product": "whatsapp",
              "call_id": call_id,
               "action": action,
               "session": {
                 "sdp_type": sdp_type,
                 "sdp":  sdp
               }
            }

        console.log( f"{body}" )

        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/calls"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {await env.META.get('USER_TOKEN')}"
        }
        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {await env.META.get('USER_TOKEN')}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return





#Envía un template say_atender buy_order que responde con un botón que lleva buy_order
#Ese botón, permite a un colaboraodr tomar la orden dada por buy_order
async def say_atender( env, wa_id, taker_fono, nombre, descripcion, comuna, buy_order ):
        console.log("En say_atender")
        console.log(f"wa_id {wa_id}")
        console.log( f"descripcion  {descripcion}")
        #-cuando no tenga saldo la imagen deb ser ilustrativa de los pasos para lograr 
        if await get_saldo(env, wa_id) > 0:
          imagen_url = f"{env.API_URL}/{env.TAKEME_IMAGE_PATH}"
        else:
          imagen_url = f"{env.API_URL}/{env.FIRST_TAKEME_IMAGE_PATH}"

        console.log(f"imagen_url {imagen_url}")
        

        body =  { "messaging_product": "whatsapp",
                   "to": wa_id,
                   "type": "template",
                   "template": { "name": "say_atender",
                                 "language": {"code": "es"},
                    "components": [
                   { "type": "body",
                     "parameters": [
                         { "type": "text", "parameter_name": "nombre", "text": nombre },
                         { "type": "text", "parameter_name": "reporte", "text": descripcion },
                         { "type": "text", "parameter_name": "comuna", "text": comuna }
                     ]
                   },
                   { "type": "header",  "parameters": [
                    { "type" : "image",
                     "image": { "link": imagen_url } } ] }
                     ] } }

        console.log( f"{body}" )

        bearer, phone_id = await get_bearer_and_phone(env, False)

        uri     = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
        
        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {bearer}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        result_dict = json.loads( result )
        id = result_dict['messages'][0]['id']
        console.log(f"id {id}")
        try:
          await env.DICT.put( id, buy_order, { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION } )
        except:
          pass


        return


#Envía un template say_tomar_buy_order que responde con un botón que lleva buy_order
#Ese botón, permite a un colaboraodr tomar la orden dada por buy_order
async def say_atender_antiguo( env, wa_id, taker_fono, nombre, descripcion, comuna, buy_order ):
        console.log("En say_atender")
        console.log(f"wa_id {wa_id}")
        console.log( f"descripcion  {descripcion}")
        imagen_url = f"{env.API_URL}/{env.TAKEME_IMAGE_PATH}"


        body =  { "messaging_product": "whatsapp",
                   "to": wa_id,
                   "type": "template",
                   "template": { "name": "say_atender",
                                 "language": {"code": "es"},
                    "components": [
                   { "type": "body",
                     "parameters": [
                         { "type": "text", "parameter_name": "nombre", "text": nombre },
                         { "type": "text", "parameter_name": "reporte", "text": descripcion },
                         { "type": "text", "parameter_name": "comuna", "text": comuna }
                     ]
                   },
                   { "type": "header",  "parameters": [
                    { "type" : "image",
                     "image": { "link": imagen_url } } ] },
                    { "type": "button", "sub_type": "url", "index": "0", 
                     "parameters": [ { "type": "text", "text": f"{buy_order}&fono_colaborador={taker_fono}" } ] } ] } }

        console.log( f"{body}" )

        uri     = f"https://graph.facebook.com/v23.0/{env.PHONE_NUMBER_ID}/messages"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {await env.META.get('USER_TOKEN')}"
        }
        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {await env.META.get('USER_TOKEN')}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        result_dict = json.loads( result )
        id = result_dict['messages'][0]['id']
        console.log(f"id {id}")
        try:
          await env.DICT.put( id, buy_order, { 'expirationTtl': env.SEGUNDOS_DE_EXPIRACION } )
        except:
          pass


        return



async def say_pagar_visita( env, wa_id, nombre, amount, path_de_pago ):
        console.log("En say_pagar_visita")
        console.log(f"wa_id {wa_id}")
        console.log( f"amount  {amount}")
        console.log( f"nombre  {nombre}")
        console.log( f"link_de_pago  {path_de_pago}")

        imagen_url = f"{env.API_URL}/{env.JEFE_IMAGE_PATH}"

        body = {"messaging_product"    :  "whatsapp", 
                "to"                   :  wa_id,
                "type"                 : "template",
                "template"             : { "name" : "say_pagar",
                                       "language" : { "code" : "es" },
                "components"           : [
                { "type": "header",  "parameters": [
                   { "type" : "image",
                     "image": { "link": imagen_url } } ] },
                { "type" :   "body", "parameters" : [
                    { "type"            :   "text", "parameter_name": "nombre",   "text" : nombre   } ,
                    { "type"            :   "text", "parameter_name": "amount", "text" : amount } ] },
                { "type"    : "button",
                     "sub_type": "url",
                     "index"   : "0",
                   "parameters": [ { "type": "text", "text": path_de_pago}]}]}}

        bearer, phone_id = await get_bearer_and_phone( env, True)

        uri     = f"https://graph.facebook.com/v23.0/{phone_id}/messages"

        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {bearer}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        console.log(f"body {body}")
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return






async def say_link_de_pago( env, wa_id, nombre, amount, path_de_pago ):
        console.log("En say_link_de_pago")
        console.log(f"wa_id {wa_id}")
        console.log( f"amount  {amount}")
        console.log( f"nombre  {nombre}")
        console.log( f"link_de_pago  {path_de_pago}")

        imagen_url = f"{env.API_URL}/{env.TAKEME_IMAGE_PATH}"


        body = {"messaging_product"    :  "whatsapp",
                "to"                   :  wa_id,
                "type"                 : "template",
                "template"             : { "name" : "say_pagar",
                                       "language" : { "code" : "es" },
                "components"           : [
                { "type": "header",  "parameters": [
                   { "type" : "image",
                     "image": { "link": imagen_url } } ] },
                { "type" :   "body", "parameters" : [
                    { "type"            :   "text", "parameter_name": "nombre",   "text" : nombre   } ,
                    { "type"            :   "text", "parameter_name": "amount", "text" : amount } ] },
                { "type"    : "button",
                     "sub_type": "url", 
                     "index"   : "0",
                   "parameters": [ { "type": "text", "text": path_de_pago}]}]}}

        bearer, phone_id = await get_bearer_and_phone( env, True)

        uri     = f"https://graph.facebook.com/v23.0/{phone_id}/messages"

        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {bearer}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }

        console.log(f"body {body}")
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return


async def say_link_de_recarga( env, wa_id, nombre, amount, path_de_pago ):
        console.log("En say_link_de_recarga")
        console.log(f"wa_id {wa_id}")
        console.log( f"amount  {amount}")
        console.log( f"nombre  {nombre}")
        console.log( f"link_de_pago  {path_de_pago}")

        imagen_url = f"{env.API_URL}/{env.TAKEME_IMAGE_PATH}"


        body = {"messaging_product"    :  "whatsapp",
                "to"                   :  wa_id,
                "type"                 : "template",
                "template"             : { "name" : "say_recargar",
                                       "language" : { "code" : "es" },
                "components"           : [
                { "type": "header",  "parameters": [
                   { "type" : "image",
                     "image": { "link": imagen_url } } ] },
                { "type" :   "body", "parameters" : [
                    { "type"            :   "text", "parameter_name": "precio", "text" : amount } ] },
                { "type"    : "button",
                     "sub_type": "url",
                     "index"   : "0",
                   "parameters": [ { "type": "text", "text": path_de_pago}]}]}}

        bearer, phone_id = await get_bearer_and_phone( env, False)

        uri     = f"https://graph.facebook.com/v23.0/{phone_id}/messages"

        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {bearer}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }
        console.log(f"body {body}")
        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return


async def send_msg( env, wa_id, msg, cliente):
        console.log( "En send_msg")
        console.log(f"wa_id {wa_id}")
        console.log( f"msg  {msg}")

        if cliente:
          bearer, phone_id = await get_bearer_and_phone( env, True)
        else:
          bearer, phone_id = await et_bearer_and_phone( env, False)

        uri     = f"https://graph.facebook.com/v23.0/{phone_id}/messages"
        
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
                 "Authorization": f"Bearer {bearer}",
                 "content-type": "application/json;charset=UTF-8"
               },
        }

        response = await fetch(uri, to_js(options))
        console.log(f"response {response}")
        content_type, result = await gather_response(response)
        console.log(f"result {result}")
        return Response( msg, status="200")


#sujeto a eror de reenganche en waba
async def send_reply( env, wa_id, reply, cliente):

        bearer, phone_id = await get_bearer_and_phone(env, cliente)

        uri     = f"https://graph.facebook.com/v23.0/{phone_id}/messages"

        body = {
                    "messaging_product" :  "whatsapp",
                    "recipient_type"    :  "individual",
                    "to"                :  wa_id,
                    "type"              :  "text",
                    "text"              :  { "preview_url" : True,
                                                     "body": reply }
        }
        options = {
               "body": json.dumps(body),
               "method": "POST",
               "headers": {
                 "Authorization": f"Bearer {bearer}",
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
          <h2 class='pb-3 align-left mbr-fonts-style display-2'>Visita de Electricista a Domicilio</h2>
          <div>
            <div class='icon-block pb-3'>
              <span class='icon-block__icon'>
              <span class='mbri-letter mbr-iconfont'></span>
              </span>
              <h4 class='icon-block__title align-left mbr-fonts-style display-5'>Este servicio tiene un costo de:</h4>
              <div class='col-md-4' data-for='amount'>
                <input type='text' readonly='' value = {env.PRECIO_VISITA} class='form-control input' id='amount' name='amount' data-form-field='amount' placeholder='Monto a Pagar' required=''>
              </div>
            </div>
        </div>


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
                <textarea class="form-control input" name="descripcion" rows="3" data-form-field="Descripcion" placeholder="Describa su problema e indique si está limitado en presupuesto y cuándo es lo máximo que está disponible." style="resize:none" required="" id="message-form4-8e"></textarea>
              </div>
              <div hidden="" class="container">
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
                <input type="text" readonly="" hidden="" value = {env.PRECIO_VISITA} class="form-control input" id="amount" name="amount" data-form-field="amount" placeholder="Monto a Pagar" required="">
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


