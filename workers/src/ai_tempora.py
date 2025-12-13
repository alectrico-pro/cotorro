async def alec_ai( env, wa_id):


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

                        presentacion="""Te llamas alexo y eres el asistente de la plataforma alectrico, la cual contacta en Providencia, Chile a las personas con electricistas a domicilio.
En primero lugar debes conseguir una ficha con los siguientes datos:

1. Nombre
2. Teléfono
3. Comuna
4. Dirección
5. email

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

                        await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":system",     mensaje_inicial )
                        await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":user" , mensaje_colaborador )

                        dico =  {
                         'max_tokens': 502,
                         'messages': [ { 'role': 'system', 'content': presentacion },
                                       { 'role': 'system', 'content': 'No haga suposiciones sobre los valores, pregunte si es necesita aclararlos.' },
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
                        mensajes = []
                        mensaje_colaborador = json.dumps( { 'role': 'user', 'content': descripcion } )
                        mensajes_anteriores = await env.DIALOGO.list( prefix = f"{ fono }:no_colaborador" )
                        mensajes.append( { 'role': 'user', 'content': descripcion } )

                        for key in mensajes_anteriores.keys.sort():
                           value = await env.DIALOGO.get(key.name)
                           mensaje_dict = json.loads(value)
                           role    = mensaje_dict['role']
                           content = mensaje_dict['content']
                           console.log(f"{role}{content}")
                           mensajes.append( mensaje_dict )

                        dico_con_tools =  {
                         'max_tokens': 502,
                         'messages': mensajes,
                         'tools':    [
                                       {      'name': 'cuestionario',
                                       'description': 'Enviar Cuestionario',
                              'parameters': { 'type': 'object',
                                         'properties': {'nombre'  :
                                                           {'type': 'string',
                                                       "minLength": 1,
                                                         'default': nombre,
                                                     'description': "Nombre de la persona que llenará el cuestionario." }}}},
                                       {      'name': 'sugerir_electricista',
                                       'description': 'Sugerir Electricista.' },
                                       {      'name': 'enviar_aviso',
                                       'description': 'Avisar a electricistas.',
                               'parameters': { 'type': 'object',
                                         'properties': {   'orden': {'type': 'string',
                                                     'description': "Número de la orden de servicio",
                                                         'default': str( random.randint(1, 10000)) },
                                                          'nombre': {'type': 'string',
                                                       "minLength": 1,
                                                     'description': "Nombre de la personas que recibirá al electricista"},
                                                       'telefono': {'type': 'string',
                                                       "minLength": 1,
                                                     'description': 'Teléfono de contacto al que debe llamar el electricista.'},
                                                           'email': {'type': 'string',
                                                       "minLength": 1,
                                                     'description': 'Dirección de correo electróncao para recibir el contrato y cualquier otra documentación.'},
                                                       'direccion': { 'type': 'string',
                                                       "minLength": 1,
                                                         'default': 'no-indica',
                                                          'comuna': 'Dirección del usuario.'},
                                                       'comuna': {'type': 'string',
                                                       "minLength": 1,
                                                          'comuna': 'Comuna hacia donde se debe dirigir el electricista'},
                                                     'descripcion': {'type': 'string',
                                                       "minLength": 1,
                                                     'description': 'Descripción del problema.'}
                                                      },
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
                        if False:
                         dico =  {
                         'max_tokens': 502,
                         'messages': [ { 'role': 'system', 'content': 'No haga suposiciones sobre los valores, pregunte si es necesita aclararlos.' },
                                       { 'role': 'user',   'content': descripcion }]}
                         result = await env.AI.run( await env.I.get('MODELO'), to_js( dico))
                         mensaje_assistant = json.dumps( { 'role': 'assistant', 'content': result.response  } )
                         await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":assistant" , mensaje_assistant )
                         if result and result.response:
                            mensaje_gerente =  json.dumps( { 'role': 'assistant', 'content': result.response })
                            await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":assistant" , mensaje_gerente )
                            reply = (
                            f"{result.response} \n"
                            "..................... \n "
                            "Escriba *xxx* para terminar \n "
                            )
                            await send_reply(env, wa_id,  reply, True )

                      if True:
                         try:
                          result = await env.AI.run(await env.I.get('MODELO'), to_js (dico_con_tools ) )
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
                                     console.log(f"call orden {call.orden}")
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

                                     tool_resultado = json.dumps( { 'role': 'tool', 'content': resultado  } )
                                     await env.DIALOGO.put( str(fono) + ":no_colaborador" + str(datetime.now()) + ":tool" , tool_resultado )
                                     dico =  {
                                       'max_tokens': 502,
                                       'messages': [ { 'role': 'user',   'content': tool_resultado }]}
                                     result = await env.AI.run(await env.I.get('MODELO'), to_js (dico ) )
                                     if result and result.response:
                                        console.log(f"{result.response}")
                                        reply = (
                                        f"{result.response} \n"
                                        "..................... \n "
                                        "Escriba *xxx* para terminar \n "
                                        )
                                        await send_reply(env, wa_id,  reply, True )

                                        await env.DIALOGO.put( str(fono) + ":" + "no_colaborador" +  str(datetime.now()) + ":user" , mensaje_colaborador )
                                        mensaje_gerente =  json.dumps( { 'role': 'assistant', 'content': result.response })
                                        await env.DIALOGO.put( str(fono) + ":" + "no_colaborador" +  str(datetime.now()) + ":assistant" , mensaje_gerente )
                         except Exception as e:
                           console.log(f"Error {e}")
                      #envia muchos,no sé por qué
                        if False and 'tokens' in  mensaje_gerente and False:
                             buy_order   = str( random.randint(1, 10000))
                             #await save_text_message(env, id, wa_id, buy_order, descripcion, amount)
                             path_de_pago = f"/transbank?amount={env.PRECIO_PROCESO}&session_id={wa_id}&buy_order={buy_order}"
                             try:
                               await say_link_de_pago( env, wa_id, '\uD83D\uDE01',  env.PRECIO_PROCESO, path_de_pago )
                             except:
                               pass
                             await difundir_a_colaboradores(env, buy_order, nombre, descripcion, 'no-indica' , wa_id, 'user@alectrico.cl', 'no-indica', env.PRECIO_TOKEN)

                             await enviar_template_say_visita_flow_reserva( request, env, wa_id )

                        return Response( "Es Colaborador", status="200")

