#Envía un mensaje a usuarios fuera de la ventana
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


