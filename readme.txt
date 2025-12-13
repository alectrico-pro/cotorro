Cotorro es un worker que recibe solicitudes de clientes y las distribuye a colaboradores.

Usa solament cloudflae y facebook meta api para conseguir esto.

0. Tareas manuales
  1. Renovar mensualment el token de META
    Debe irse a developer.facebook.com y generar nuevo token temporal
    Luego ir a curl e ingresar ese token en el script curl alargar_token
    Obtener el token alargado y escribrilo en wrangler.toml para los dos workers
    Actualizar set_token_env
    Llamar a set_token_env para que se actualice la variable de ambiente token_cotorro

1. Elementos
  Patrones de Mensajes de META API (messages templates)
    Cuenta Whatsapp WABA 932... en suspenso hasta que se salde la deuda de 25 dólares
    Cuenta Whatsapp WABA 945
      Template Atender
       
2. Elementos Cloudflare
    Cuenta ventas@alectrico.cl
     Compute workers
      A. Worker python cotorro
        https://www.alectrico.cl
         Presenta formulario para ingresar datos de una visita a domicilio
          Registra esos datos en KV BUY_ORDER pedidos
          El cliente es redirigido a pagar y esto lleva a www.alectrico.cl/agender desde donde parte el worker cotorro
        https://api.alectrico.cl
          Se usa para recibir los callbacks de pago
            transbank
              genera el link de pago y luego redirige a ese url
            return_url
              recibe respuestas positivas o negativas desde transbank
        https://repair.alectrico.cl     
            hace lo mismo que www.alectrico.cl

       B. Worker python financiero
        https://recarga.alectrico.cl
     KV
      BUY_ORDER
       Anota los pedidos que se hayan iniciado, desde diferentes endpoints: alectrico.cl/agendar, /create_from_landing_page
      FINANCIERO
       Anota los pagos de los colaboradores
       Soporta los tokens que esto hayan comprado
      NOMINA
       Contiene los fonos  y nombres de los colaboradores
        Se debe entrar a Cloudflare para ingresar nuevos colaboradores
      ASSETS
       Contienen imágenes y otros assets
       Se invoca desde webhook asociado a app Meta Cotorro
         url  webhook 

3. Deployment
    Repositorio alectrico-pro/cotorro
      requiere ssh key en .ssh
      usar make push de docker-data/aureo/server
    Ubicaciones
      worker cotorro 
        docker-data/orquestados/workers/cotorro
      worker financiero
        docker-data/orquestados/workers/cotorro/workers/financiero

    Importante
      wrangler.toml en ambos workers usan las mismas configuraciones de META_TOKEN, KVS y otros
   
4. Atender
     alectrico.cl/atender
     Concreta el valor de negocio, reacciona a un llamado desde un reply atender desde un template message que tenga un botón Atender
       Busca tokens válidos para el wa_id que haya recibido el template
       Lo usa (lo borra)
       Redirige al user a la página de canje
         Hay tres resultados
           La orden de compra para este atender ya no está vigent
           Existe la orden de compra pero este wa_id no tiene tokens pagados vigentes
           Existe todo lo anterior
             Se entrega el fono del cliente, a través de la pantalla
         
