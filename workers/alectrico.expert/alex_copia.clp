;#encoding: utf-8
;;;================================================================
;;;     Especialista em Fallas Eléctricas
;;;
;;;     
;;;     Este programa pretende diagnosticar Fallas Eléctricas
;;;     
;;;     Eng. Conhecimento: Alexander Espinosa
;;;     Especialista:      Prof. Carlos Niño
;;;
;;;     
;;;================================================================

(defmodule MAIN (export ?ALL))

;;****************
;;* DEFFUNCTIONS *
;;****************
 ; Este es o principal elemento de interface todo mundo usa
 (deffunction MAIN::fazer-pergunta (?pergunta ?valores-permitidos ?porquetitulo ?porque ?unidad)
       (if (member entero ?valores-permitidos)  ;esto es para los atributos marcados como números enteros
         then

           (printout t crlf ?pergunta crlf "unidad de medida: " ?unidad "    ") (bind ?resposta (read))
            (while (and (not (numberp ?resposta)) (not (eq . ?resposta))) do
               (if (lexemep ?resposta) then (bind ?resposta (lowcase ?resposta)))
               (if (eq ?resposta p) then (printout t "programa parado por orden del usuario" crlf) (break))
               (if (eq ?resposta f) then (printout t "intentando um diagnóstico por orden del usuario" crlf) (break))
               (if (eq ?resposta porque)  then (printout t ?porquetitulo crlf) (printout t "RESPUESTA: " ?porque  crlf crlf))
               (printout t ?pergunta crlf "**   ")  (bind ?resposta (read)))

	 else

	   (printout t crlf ?pergunta crlf "**   ") (bind ?resposta (read))
	   (while (not (member ?resposta ?valores-permitidos)) do
	       (if (lexemep ?resposta) then (bind ?resposta (lowcase ?resposta)))
	       (if (eq ?resposta p) then (printout t "programa parado por orden del usuario" crlf) (break))
	       (if (eq ?resposta f) then (printout t "intentando um diagnóstico por orden del usuario" crlf) (break))           

	       (if (eq ?resposta porque)  then (printout t ?porquetitulo crlf) (printout t "RESPUESTA: " ?porque  crlf crlf))
	       (printout t ?pergunta crlf "**   ")  (bind ?resposta (read)))  
	 )
	 ?resposta
         )

;;************
;;* ESTADO 0 *
;;************

 (deftemplate MAIN::atributo
   (slot nome)
   (slot valor)
   (slot unidad)
   (slot certeza (default 100.0))
   (multislot porque)
   )


  ;este aqui es o readme
 (defrule MAIN::app
 (declare (salience 10000))
 ?f1<-(initial-fact)
  =>   
   (printout t crlf )
   (printout t "-----ALEX:Aléctrico Expert. Diagnóstico Inteligente de Fallas Eléctricas-------------" crlf)
   (printout t "A seguir será presentonces un cuestionario que será usado para inferir cual" crlf)
   (printout t "es el tipo de falla presente en una instalación eléctrica."  crlf)
   (printout t "Para responder debe digitar una de las alternativas encerradas con estos paréntesis <>" crlf)
   (printout t "Se no supiese una respuesta, responda digitando un punto <.>. "  crlf)
   (printout t "De esa forma se abrirán posibilidades para que otros  " crlf)
   (printout t "se puedan probar otros diagnósticos en paralelo" crlf crlf)
   (printout t "Digite <porque> para saber la justificación de cada pregunta " crlf)
   (printout t "Para ayuda al responder una pregunta digite <?>" crlf)
   (printout t "Presione <f> en cualquier momento para forzar un diagnóstico" crlf)
   (printout t "con los hechos disponibles en ese momento" crlf)
   (printout t "Presione <p> para abandonar el cuestionario" crlf crlf)
   
  )
  
  
 ; o inicio es o mais prioritario, estabelece algumas variáveis e estabelece uma sequencia de focos
 (defrule MAIN::inicio
  (declare (salience 1000))
  =>
  (set-fact-duplication TRUE)
  (assert (eliminar-diagnosticos-pouco-fundados))
  (assert (combinar-incertezas-que-levam-ao-mesmo-diagnostico)) 
  (printout t "Presione c para comenzar" crlf "**   ")  
  (bind ?resposta (read))
  (if (eq ?resposta p) 
      then (printout t "programa parado" crlf)
      else e
          (printout t crlf crlf crlf crlf crlf crlf crlf)      
          (dribble-on salida.txt) 
          (focus REGLAS-PERGUNTAS REGLAS MEDICIONES PERCORRER-ARVORE REGLAS IMPRIMIR))
  )

 ; Este es o principal elemento que permite utilizar incertezas no diagnóstico atravess dos graus
 ; de crenca que o usuario tem sobre os fatos e o especialista sobre as regras
 ; a combinação pode ser desativada com a bandeira (combinar-......)
 ; Quando a combinação es desativada podem ser mostrados diagnosticos iguais com diferentes
 ; graus de creenca. Quando ativada, um diagnostico pode ser fortalecido com regras que conduzem
 ; a ele por diferentes caminhos. 
 (defrule MAIN::combinar-incertezas 
 (declare (salience 100) (auto-focus TRUE))
    (combinar-incertezas-que-levam-ao-mesmo-diagnostico) 
    ?rem1 <- (atributo (nome ?rel) (valor ?val) (certeza ?per1)(porque ?oporque1))
    ?rem2 <- (atributo (nome ?rel) (valor ?val) (certeza ?per2)(porque ?oporque2))
    (test (neq ?rem1 ?rem2))
    =>    
    ;(bind ?dd ?oporque1  -OU- ?oporque2)
    (bind ?dd (str-cat ?oporque1 " ADEMAS DE " ?oporque2))
    (retract ?rem1)
   ; (printout t ?dd crlf) (read)
    (modify ?rem2 (certeza (/ (- (* 100 (+ ?per1 ?per2)) (* ?per1 ?per2)) 100))
                  (porque ?dd)
    )   
    )
  



 ;;***************************************************************************************
 ;; REGLAS SINTATICAS PARA ANALIZAR AS REGLAS DO ESPECIALISTA IMPLEMENTA GRAUS DE CRENCA *
 ;;***************************************************************************************
 ; estas regras operam sobre os strings a fim de realizar uma análise sentática e lógica do 
 ; que neles foi expresso. E desta forma que a arvore de solução de problemas es percorrida
 
(defmodule REGLAS (import MAIN ?ALL) (export ?ALL))
  
 (deftemplate REGLAS::regra
    (slot certeza (default 100.0))
    (multislot si)
    (multislot entonces)
    (slot porque)
    )
  
  ;sentactico pop e push
 (defrule REGLAS::eliminar-Es-nos_antecedentes
    ?f <- (regra (si e $?rest))
    =>
    (modify ?f (si ?rest)))
    

  ; parecido ao anterior, mas nos consequentes  
 (defrule REGLAS::eliminar-Es-nos-consequentes
    ?f <- (regra (entonces e $?rest))
    =>
    (modify ?f (entonces ?rest)))
  
 ; logico pop
 (defrule REGLAS::eliminar-es-quando-satisfeito
    ?f <- (regra (certeza ?c1) 
                 (si ?atributo es ?valor $?rest))
    (atributo (nome ?atributo) 
              (valor ?valor) 
              (certeza ?c2))
    =>
    (modify ?f (certeza (min ?c1 ?c2)) (si ?rest)))
  ;logico pop


 (defrule REGLAS::eliminar-no-es-quando-satisfeito
    ?f <- (regra (certeza ?c1) 
                 (si ?atributo no-es ?valor $?rest))
    (atributo (nome ?atributo) 
              (valor ~?valor) 
              (certeza ?c2))
    =>
    (modify ?f (certeza (min ?c1 ?c2)) (si ?rest)))

  ;obter valores utilizando grausde crença
 (defrule REGLAS::produzir-o-consequente-da-regras-com-graus-de-creenca
    ?f <- (regra (certeza ?c1) 
                 (si) 
                 (porque ?porque)
                 (entonces ?atributo es ?valor com certeza ?c2 $?rest))
    =>
    (modify ?f (entonces ?rest))
    (assert (atributo (nome ?atributo) 
                      (valor ?valor)
                      (porque ?porque)
                      (certeza (/ (* ?c1 ?c2) 100)))))
    



                   
  ;obeter valores crispy 
 (defrule REGLAS::produzir-o-consequente-da-regra-com-100-crenca
    ?f <- (regra (certeza ?c1)
                 (si)
                 (porque ?porque)
                 (entonces ?atributo es ?valor $?rest))
    (test (or (eq (length$ ?rest) 0)
              (neq (nth 1 ?rest) com)))
    =>
    (modify ?f (entonces ?rest))
    (assert (atributo (nome ?atributo) 
                      (valor ?valor) 
                      (porque ?porque)
                      (certeza ?c1))))
                      
                      


  ;obeter valores crispy 
 (defrule REGLAS::negar-reglas-no-es
    ?f <- (regra (si ?atributo no-es ?valor))
    =>
    (modify ?f (si not ?valor)))


;;**************************************************
;;* REGLAS DE PROCESAMIENTO DE MEDICIONES          *
;;**************************************************

(defmodule MEDICIONES (import REGLAS deftemplate ?ALL) (import MAIN deftemplate ?ALL) (export ?ALL))

(deffacts reglas-de-procesamiento-de-mediciones

   (regra (si sensibilidad-diferencial es 30 )
          (entonces corriente-de-falla es limitada com certeza 20)
          (porque "porque 30 mA durante no más de 30ms es suficiente para evitar ataques al corazón")
          )


  (regra (si sensibilidad-diferencial es 30 )
          (entonces corriente-de-falla es limitada com certeza 100)
          (porque "porque 30 mA por no más de 30ms es suficiente para evitar ataques al corazón")
          )

  

   (regra (si diferencial-doble-polo es existente e puesta-a-tierra es inexistente e conexion-a-plomeria es conectado)
          (entonces corriente-de-falla es baja e tension es segura com certeza 20 e tension es normal com certeza 20 e tension es peligrosa com certeza 20)
	  (porque "porque el diferencial-doble-polo no necesita que haya una puesta a tierra para despejar rápidamente la energía, basta que la tierra esté conectada a las tuberías de la plomería o que el camino de la corriente existe de alguna forma.")
	  )

   (regra (si sensibilidad-diferencial es 300 )
          (entonces corriente-de-falla es poco-limitada com certeza 20)
          (porque "porque 300 mA es una sensibilidad adecuada para circuitos públicos no para domicilios")
          )
      
   (regra (si sensibilidad-diferencial es 300000000 )
          (entonces corriente-de-falla es ILIMITADA com certeza 100)
	  (porque "porque 300000000 mA es un valor muy grande")
 )

)

(defrule MEDICIONES::evalua-medicion-de-tierra-cuando-no-necesita-diferencial
     (atributo (nome resistencia-de-tierra)
               (valor ?valor&:(and (numberp ?valor) (> ?valor 2) and (< ?valor 6)))
               )
  =>
   (assert (atributo (nome tension)
                     (valor segura)
                     (certeza 100)
                     (porque "porque la puesta a tierra es de muy buena calidad. En este caso las fallas a tierra de los equipos serán capaces de hacer disparar a las protecciones de sobreintensidades y no habrá sobretensiones peligrosas porque la energía siempre encontrará un camino expedito a tierra.")
           ))
   (assert (atributo (nome resistencia-de-tierra)
                     (valor baja)
                     (certeza 100)
                     (porque "porque sería capaz de disparar las protecciones contra sobretensiones")))

   (assert (atributo (nome  corriente-de-falla)
                     (valor alta)
                     (certeza 20)
                     (porque "porque la resistencia de tierra es baja") 
           )
   )
                     
)

(defrule MEDICIONES::evalua-medicion-de-tierra-cuando-es-sospecha-que-se-falsa
   ?tierra <- (atributo (nome resistencia-de-tierra)
                        (valor ?valor&:(and (numberp ?valor) (< ?valor 2)))
               )
   ?puesta <- (atributo (nome puesta-a-tierra)
                        (valor existente)
                        )
  =>
   (modify ?tierra (valor 10000000) (porque "porque el valor ingresado es falso y se ha supuesto que en realidad no existe la puesta a tierra" ))
   (assert (atributo (nome tarea)
                     (valor diferencial)
                     (porque "porque se reportó una resistencia de puesta a tierra de RA < 2 ohm, pero es un valor demasiado bueno para ser cierto, así que se supone que es falso y se cambia al mayor valor posible.")))
   (assert (atributo (nome tarea)
                     (valor puesta-a-tierra)
                     (porque "porque se reportó un valor falso para la puesta a tierra de proteccioń, así que se asume que la puesta a tierra no existe")))

   (modify ?puesta (valor inexistente))
)


(defrule MEDICIONES::evalua-demora-diferencial-cuando-es-menor-igual-que-30
    (atributo (nome demora-de-diferencial )
              (valor ?mSegundos&:(and (numberp ?mSegundos) (<= ?mSegundos 30  ) ))
              (certeza ?certeza-demora)
              )
 =>
  (assert ( atributo (nome tiempo-de-falla)
                     (valor limitado)
                     (certeza ?certeza-demora)
                     (porque "porque la demora es menor que lo necesario para que produzca ataques al corazón en las personas")
           )
))

(defrule MEDICIONES::evalua-demora-diferencial-cuando-mayor-a-30
    (atributo (nome demora-de-diferencial )
              (valor ?mSegundos&:(and (numberp ?mSegundos) (> ?mSegundos 30)))
              (certeza ?certeza-demora)
              )
 =>
  (assert ( atributo (nome demora-de-diferencial)
                     (valor excesiva)
                     (certeza ?certeza-demora)
                     (porque "porque la demora permite ataques al corazón en las personas")
                     ))
  (assert ( atributo  (nome tarea)
                     (valor cambiar-diferencial-por-uno-de-30-ms)
                     (certeza ?certeza-demora)
                     (porque "porque el diferencial existente permite ataques al corazón en las personas")
                     ))
) 


(defrule MEDICIONES::evalua-sensibilidad-diferencial
    (atributo (nome sensibilidad-diferencial )
              (valor ?mAmperes&:(numberp ?mAmperes))
              (certeza ?certeza-diferencial-doble-polo)
              )
    (atributo (nome tension-de-seguridad)
              (valor ?tension&:(numberp ?tension))
              (certeza ?certeza-tension-seguridad)
              )
   ?tierra <- (atributo (nome resistencia-de-tierra)
              (valor ?Rmedida&:(numberp ?Rmedida))
              (certeza ?certeza-resistencia-de-tierra)
              )
 =>
    (assert (atributo (nome resistencia-de-puesta-a-tierra)
                       (valor ?Rmedida)
		       (certeza 100)
		       (porque "porque se asume igual que la resistencia de loop, con un margen de error a favor.")
	    )
    )
    (bind ?Rrequerida (* (float 1000) (/ (float ?tension) (float ?mAmperes))  ))
    (format t " Dada la sensibilidad del diferencial-doble-polo, se require una Resistencia de circuito de falla menor a --%d- ohm %n" ?Rrequerida)
    (if (> ?Rrequerida ?Rmedida ) 
    then
    (format t " Rrequerida > Rmedida. Se obtiene que  %d > %d ¡Felicitaciones ! %n" ?Rrequerida ?Rmedida)

    (assert (atributo (nome tension)
                      (valor segura) 
		      (certeza (min ?certeza-resistencia-de-tierra ?certeza-tension-seguridad ?certeza-diferencial-doble-polo))
		      (porque "porque la resistencia de loop medida es menor que lo que require el voltaje de seguridad dada la sensibilidad del diferencial-doble-polo" )))   
    (assert (atributo (nome resistencia-de-falla)
                      (valor suficiente)
                      (certeza (min ?certeza-resistencia-de-tierra ?certeza-tension-seguridad ?certeza-diferencial-doble-polo))
                      (porque "porque la resistencia de loop medida es menor que lo que require el voltaje de seguridad dada la sensibilidad del diferencial-doble-polo" )))

    (assert (atributo (nome sensibilidad-diferencial)
                      (valor adecuada)
                      (certeza (min ?certeza-resistencia-de-tierra ?certeza-tension-seguridad ?certeza-diferencial-doble-polo))
                      (porque "porque la resistencia de loop medida es menor que lo que require el voltaje de seguridad dada la sensibilidad del diferencial-doble-polo" )))




    else

    (format t " Rrequerida < Rmedida. Se obtiene que  %d > %d ¡CUidado ! %n" ?Rrequerida ?Rmedida)

    (assert (atributo (nome tension)
                      (valor normal)
                      (certeza (min ?certeza-resistencia-de-tierra ?certeza-tension-seguridad ?certeza-diferencial-doble-polo))
                      (porque "porque la resistencia de loop medida es mayor que lo que require el voltaje de seguridad dada la sensibilidad del diferencial-doble-polo" )))

    (assert (atributo (nome resistencia-de-falla)
                      (valor alta)
                      (certeza (min ?certeza-resistencia-de-tierra ?certeza-tension-seguridad ?certeza-diferencial-doble-polo))
                      (porque "porque la resistencia de loop medida es mayor que lo que require el voltaje de seguridad dada la sensibilidad del diferencial-doble-polo" )))
  

    (assert (atributo (nome sensibilidad-diferencial)
                      (valor inadecuada)
                      (certeza (min ?certeza-resistencia-de-tierra ?certeza-tension-seguridad ?certeza-diferencial-doble-polo))
                      (porque "porque la resistencia de loop medida es mayor que lo que require el voltaje de seguridad dada la sensibilidad del diferencial-doble-polo" )))


    )
)
 
;;**************************************************
;;* REGLAS DE ENCADEAMENTO DE PERGUNTAS PARA FRENTE *
;;**************************************************

(defmodule PERCORRER-ARVORE (import REGLAS ?ALL)
                           ; (import REGLAS-PERGUNTAS ?ALL)
                            (import MAIN ?ALL) (export ?ALL))
 (defrule PERCORRER-ARVORE::subir-arvore 
      =>
       (focus REGLAS))


 (defrule PERCORRER-ARVORE::elimina-tiempo-de-falla-limitado
   (declare (salience 10))
   ?rem <- (atributo (nome tiempo-de-falla)
                     (valor limitado)
                     (certeza ?limitado))

           (atributo (nome tiempo-de-falla)
                     (valor excesivo)
                     (certeza ?excesivo))
   =>
    (retract ?rem)
    (printout t "Eliminado tiempo de falla limitido porque hay un reporte de tiempo de falla excesivo")
 )

 (defrule PERCORRER-ARVORE::elimina-tensiones-peligrosas
   (declare (salience 10)) ;La saliencia debe ser mayor que imprimir hechos porque imprimir hechos retracta los hechos
   ?rem <- (atributo (nome tension)
                     (valor peligrosa)
                     (certeza ?peligrosa)
                     (porque ?porque1)
                     )
           (atributo (nome tension)
                     (valor segura)
                     (certeza ?segura)
                     (porque ?porque2)
                     )
           (test (> ?segura ?peligrosa) )

   =>
   (printout t "Se eliminó la tensión peligrosa porque la credibilidad de la tensión segura es mayor" crlf)
   (retract ?rem))



 (defrule PERCORRER-ARVORE::eliminar-tensiones-normales
   (declare (salience 10)) ;La saliencia debe ser mayor que imprimir hechos porque imprimir hechos retracta los hechos
   ?rem <- (atributo (nome tension)
                     (valor peligrosa)
                     (certeza ?normal)
                     (porque ?porque1)
                     )
           (atributo (nome tension)
                     (valor segura)
                     (certeza ?segura)
                     (porque ?porque2)
                     )
           (test (> ?segura ?normal) )

   =>
   (printout t "Se elimina la tensión normal porque la credibilidad de la tensión segura es mayor" crlf)
   (retract ?rem))




 (deffacts regras-da-arvore


   (regra (si diferencial-doble-polo es existente e neutralizacion es existente)
          (entonces tarea es unir-o-verificar-neutro-a-tierra-antes-del-diferencial)
	  (porque "porque así lo recomienda la Guía Legrand pag 183. Atención, al poner el neutro a tierra, todo el exceso de energía de los vecinos (de transformador) irá a tierra en la puesta a tierra, así que el conductor de puesta a tierra de servicio debe ser grueso lo suficiente.")
	  )
  
   (regra (si tierra-de-servicio es inexistente)
          (entonces tarea es tierra-de-servicio)
          (porque "porque la tierra de servicio es un requisito oligatorio de cualquier instalación eléctrica")
          )

;---- 41 hechos, con lo nebulosos
   (regra (si regimen-neutro es TT)
          (entonces definicion es neutro-a-tierra:masas-a-tierra)
          (porque "porque se conecta el neutro del transformador de distribución a tierra  y se conectan las masas de los equipos también a tierra, a través de un cable de protección que se pone a tierra o usando un cable que se usa como neutro y tierra. El régimen TT limita la corriente de falla debido a que el circuito de falla se establece a través de la tierra. Esto puede hacer que aparezcan tensiones peligrosas si no se usan diferenciales, los que abrirían el circuito de falla a tiempo para evitar la acumulación de enerǵía y la ocurrencia de tensiones peligrosas. Esto hace que no se puedan usar las protecciones contra sobreintensidades para abrir el circuito de falla debido a que estos necesitan una gran corriente de falla para dispararse.")
          )

   (regra (si regimen-neutro es TN)
          (entonces definicion es neutro-a-tierra:masas-a-neutro)
          (porque "porque se conecta el neutro del transformador de distribución a tierra y se conectan las masas de los equipos al neutro. Las masas se conectan al neutro a través de un conductor de protección que luego se conecta al neutro, o directamente a un conductor que funciona como neutro y como conductor de proteccion. No se acepta el segundo caso en Chile.")
          )

;----fases 8 hechos

   (regra (si resistencia-de-tierra es baja e diferencial es existente)
          (entonces diferencial es innecesario-pero-exigido)
          (porque "porque la resistencia de puesta a tierra es tan baja que la función de los diferenciales las puede hacer una protección de sobreintensidas, pero la normativa lo exige de todas formas")
          )

   (regra (si intensidad-general-de-fases es equilibradas )
          (entonces tension es normal com certeza 20)
	  (porque "porque las fases están equilibradas")
          )

   (regra (si intensidad-general-de-fases es desequilibradas )
          (entonces tension es peligrosa com certeza 20 )
          (porque "porque las fases están desequilibradas")
          )

   (regra (si tensiones-de-fases es no-semejantes)
          (entonces tension es peligrosa com certeza 20)
          (porque "porque las tensiones del transformador NO son semejantes")
          )

   (regra (si tensiones-de-fases es semejantes)
          (entonces tension es normal com certeza 20)
          (porque "porque las tensiones del transformador son semejantes")
	  )

   (regra (si fases-de-enchufes es enchufes-no-alternados)
          (entonces tension es peligrosa com certeza 20) ;20 es la porción de circuitos que son enchufes, o la importancia de las cargas
          (porque "porque las fases de los enchufes NO están sincronizadas")
          )

   (regra (si fases-de-enchufes es enchufes-alternados)
          (entonces tension es normal com certeza 20) ;20 es la porción de circuitos que son enchufes, o la importancia de las cargas
          (porque "porque las fases de los enchufes están sincronizadas") 
          )

    (regra (si fases-de-iluminacion es luminarias-no-alternadas)
           (entonces tension es peligrosa com certeza 20) ;20 es la porción de circuitos que son de iluminación o la importancia de las cargas de iluminuación
           (porque "porque las fases de las luminarias NO están sincronizadas")
           )


    (regra (si fases-de-iluminacion es luminarias-alternadas)
           (entonces tension es normal com certeza 20) ;20 es la porción de circuitos que son de iluminación o la importancia de las cargas de iluminuación
           (porque "porque las fases de las luminarias están sincronizadas") 
           )

;----fallas 4 reglas

;-----incidencia de la tierra de servicio o puesta a tierra del neutro

;

   (regra (si falla es neutro-cortado e tierra-de-servicio es existente e fases-en-empalme es monofasico)
          (entonces tension es segura e energia es existente)
	  (porque "porque la energía fluirá a través de la tierra, en vez de por el neutro, que está cortado")
	  )

   (regra (si falla es neutro-cortado e tierra-de-servicio es inexistente e fases-en-empalme es monofasico)
          (entonces tension es normal e enegia ex inexistente)
	  (porque "porque no habrá una vía para que la energía retorne")
	  )

   (regra (si falla es neutro-cortado e tierra-de-servicio es inexistente e fases-en-empalme es trifasico)
          (entonces energia es existente e corrimiento-de-neutro es posible)
	  (porque "porque al cortarse el neutro, no habrá una forma de equilibrar las energías de las fases"
	  )
	  )

   (regra (si falla es neutro-cortado e fases-en-empalme es trifasico e fases es desequilibradas e neutralizacion es inexistente e puesta-a-tierra es inexistente e union-proteccion-y-neutro-en-empalme es inexistente)
          (entonces tension es peligrosa com certeza 50)
          (porque "porque el neutro está cortado, el empalme es trifasico y las fases están desequilibradas")
          )

   (regra (si falla es neutro-cortado e falla es falla-de-aislamiento e diferencial-doble-polo es existente e fases-en-empalme es monofasico)
          (entonces corriente-de-falla es limitada e tiempo-de-falla es limitado e tension es normal )
          (porque "porque el diferencial doble polo funciona con neutro cortado " )
          )

   (regra (si falla es neutro-cortado e falla es falla-de-aislamiento e diferencial-doble-polo es existente e fases-en-empalme es trifasico)
          (entonces corriente-de-falla es limitada e tiempo-de-falla es limitado e tension es peligrosa )
          (porque "porque el diferencial doble polo funciona con neutro cortado " )
          )

   (regra (si falla es neutro-cortado e falla es falla-de-aislamiento e diferencial-doble-polo es existente e puesta-a-tierra es existente e corriente-de-falla es suficiente e sensibilidad-de-diferencial es adecuada)
          (entonces corriente-de-falla es limitada e tiempo-de-falla es limitado e tension es segura)
          (porque "porque el diferencial doble polo funciona con neutro cortado y la puesta a tierra es de buena calidad lo que garantiza que el contacto indirecto se realice a una tensión segura " )
          )




   (regra (si falla es neutro-cortado e fases-en-empalme es monofasico e neutralizacion es inexistente e puesta-a-tierra es inexistente )
          (entonces tension es normal com certeza 50)
          (porque "porque el neutro está cortado y el empalme es monofasico") 
          )

;resistencia-de-tierra

   (regra (si resistencia-de-falla es baja)
	  (entonces corriente-de-falla es alta com certeza 20)
          (porque "porque la resistencia del lazo de tierra es baja") 
          )

   (regra (si diferencial-doble-polo es existente e sensibilidad-diferencial-doble-polo es adecuada e not demora-de-diferencial es excesiva)
          (entonces tiempo-de-falla es limitado com certeza 20)
          (porque "porque los diferencial-doble-polos limitan el tiempo de falla")
          )


;--- puesta a tierra 3 hechos

   (regra (si regimen-neutro es TT)
          (entonces tarea es puesta-a-tierra)
          (porque "porque el regimen de neutro TT usa una puesta a tierra de protección de las masas de los equipos")
	  )


   (regra (si regimen-neutro es TT)
          (entonces tarea es diferencial-doble-polo)
          (porque "porque el regimen de neutro TT usa una puesta a tierra de protección de las masas de los equipos, el que debe ser usado asociado a dispositivos activados por corriente de falla")
          )



   (regra (si puesta-a-tierra es inexistente e tension-en-empalme es AT e diferencial-doble-polo es inexistente)
          (entonces tension es peligrosa com certeza 20)
          (porque "porque si no hay tierra entonces la energía se acumulará en las superficies")
          )

   (regra (si puesta-a-tierra es inexistente e tension-en-empalme es BT)
          (entonces tension es normal com certeza 20)
          (porque "porque si no hay tierra entonces la energía se acumulará en las superficies")
          )


;--- diferencial-doble-polo instalado 1 hecho
   (regra (si diferencial-doble-polo es existente e sensibilidad-diferencial es adecuada e resistencia-de-falla es suficiente e not demora-de-diferencial es excesiva )
          (entonces tension es segura)
          (porque "porque se ha instalado diferencial-doble-polo con la sensibilidad adecuada y la impedancia del circuito de falla es suficiente")
          ) 

;---neutralizacion 11 hechos
   (regra (si neutralizacion es existente e resistencia-de-tierra es baja e puesta-a-tierra es existente)
          (entonces tension es segura )
          (porque "porque se ha instalado la neutralizacion y la impedancia del circuito de falla es baja")          ) 

   (regra (si regimen-neutro es TN e neutralizacion es existente e resistencia-de-falla es alta)
          (entonces proteccion es no-dispara )
          (porque "porque la corriente de falla no es grande lo suficiente para disparar las protecciones")          ) 


   (regra (si neutralizacion es existente)
          (entonces tarea es diferencial-doble-polo  )
          (porque "porque se recomienda en 9.2.7.4 instalar un sistema de dispositivos activados por corriente de falla.")
          )

   (regra (si neutralizacion es existente e fases-en-empalme es trifasico)
          (entonces tarea es tierra-de-servicio )
          (porque "porque se recomienda en 9.2.7.4 instalar un sistema que evite tensiones peligrosas en caso de corte del neutro y eso hace la puesta a tierra del neutro: refuerza el papel del neutro en su función de equilibrar las tensiones de fase en sistemas trifásicos y mantener la energía de la única fase de los sistemas monofásicos. Entonces se debe poner a tierra el neutro donde sea posible. Sin embargo esto no evita que aparezcan tensiones de 220V durante las fallas. Así que el sistema más efectivo es el empleo de diferenciales, lo que lleva a la instalación de puesta a tierra de protección, aunque estas últimas no sean tan buenas, al menos pueden cumplir con ciertos requisitos que habilitan la función de los diferenciales")
	  )
          

      (regra (si neutralizacion es existente e fases-en-empalme es monofasico)
             (entonces tarea es tierra-de-servicio )
             (porque "porque se recomienda en 9.2.7.4 instalar un sistema que evite tensiones peligrosas en caso de corte del neutro y eso hace la puesta a tierra del neutro: refuerza el papel del neutro en su función de equilibrar las tensiones de fase en sistemas trifásicos y mantener la energía de la única fase de los sistemas monofásicos. Entonces se debe poner a tierra el neutro donde sea posible.")
			            )



   (regra (si regimen-neutro es TN)
          (entonces tarea es neutralizacion)
          (porque "porque se exige en NCh 03/2004 para el régimen de neutro TN.")
          )

   (regra (si tarea es neutralizacion)
          (entonces tarea es union-proteccion-y-neutro-en-empalme  )
          (porque "porque es una exigencia para efectuar la neutralización. Ref: NCH 04/2003 9.2.7.4)")
          )

   (regra (si neutralizacion es existente e resistencia-de-falla es baja e diferencial-doble-polo es inexistente)
          (entonces diagnostico es riesgo-de-incendio com certeza 50)	  
	  (porque "porque la corriente de falla no está limitada")
	  )

   (regra (si tension es peligrosa e tiempo-de-falla-es limitado)
          (entonces diagnostico es riesgo-de-contacto-indirecto-a-tension-peligrosa  )
          (porque "de acuerdo a los hechos observados y a las reglas de conocimiento basadas en la normativa eléctrica NCh 03/2004.")
          )

   (regra (si tension es normal e tiempo-de-falla es limitado)
          (entonces diagnostico es riesgo-de-contacto-indirecto-a-tension-normal )
	  (porque "de acuerdo a los hechos observados y a las reglas de conocimiento basadas en la normativa eléctrica NCh 03/2004.")
          )

   (regra (si falla es neutro-cortado e tierra-de-servicio es existente )
          (entonces diagnostico es sin-riegos-de-contacto-indirecto e tension es segura)
	  (porque "porque la tierra de servicio ofrece un camino de retorno que sustituye al que el neutro ofrecía antes de ser cortado.")
	  )

   (regra (si tension es segura e tiempo-de-falla es limitado)
          (entonces diagnostico es sin-riesgo-de-contacto-indirecto)
          (porque "de acuerdo a los hechos observados y a las reglas de conocimiento basadas en la normativa eléctrica NCh 03/2004.")
          )

   (regra (si proteccion es no-dispara)
          (entonces diagnostico es riesgo-de-contacto-indirecto)
          (porque "porque no se activarán las protecciones en caso de falla")
          )

   (regra (si corriente-de-falla es alta)
          (entonces diagnostico es riesgo-de-incendio)
          (porque "porque la corriente de falla es alta")
          )

   (regra (si demora-de-diferencial es excesiva)
          (entonces tiempo-de-falla es excesivo)
          (porque "porque la demora del diferencial es excesiva")
          )

   (regra (si tiempo-de-falla es excesivo)
          (entonces diagnostico es riesgo-de-ataques-al-corazon)
          (porque "porque la demora del diferencial es excesiva y supera el límite médico de 30 ms")
          )

   (regra (si puesta-a-tierra es inexistente e diferencial-doble-polo es existente )
          (entonces diagnostico es riesgo-de-contacto-indirecto)
          (porque "porque el diferencial no funcionará porque no hay un retorno hacia la tierra.")
	  )
) 
  
 (deffacts regras-nebulosas  

  (regra (si tierra-de-servicio es .)
         (entonces tierra-de-servicio es existente e tierra-de-servicio es inexistente)
         (porque "porque no se conoce el valor de la tierra de servicio ")
         )

  (regra (si demora-de-diferencial es .)
         (entonces demora-de-diferencial es 30 e demora-de-diferencial es 300)
         (porque "porque no se conoce el valor de la demora del diferencial")
         )

;14 hechos
  (regra (si resistencia-de-tierra es .)
         (entonces resistencia-de-tierra es 220000000 com certeza 20  e resistencia-de-tierra es 4 com certeza 20 e tarea es medir-la-resistencia-del-lazo-de-tierra)
         (porque "porque no se conoce el valor de la resistencia a tierra")
         )

  (regra (si sensibilidad-diferencial es .)
         (entonces sensibilidad-diferencial es 30 com certeza 50 e sensibilidad-diferencial es 300000000 com certeza 50 e tarea es investigar-la-sensibilidad-del-diferencial-doble-polo) 
         (porque "porque no se conoce el valor de la sensibilidad del diferencial-doble-polo")
         )

  (regra (si tension-de-seguridad es .)
         (entonces tension-de-seguridad es 24 com certeza 100 e tension-de-seguridad es 50 com certeza 10 e tarea es decidir-cual-tension-de-seguridad-usara )
         (porque "porque no se ha especificado la tensión de seguridad")
         )

  (regra (si falla es .)
         (entonces falla es neutro-cortado com certeza 50 e
	 falla es falla-de-aislamiento com certeza 50 e tarea es investigar-que-falla-ocurrio)
	 (porque "porque no se sabe cuál es la falla"))

  (regra (si tensiones-de-fases es .)
         (entonces tensiones-de-fases es semejantes com certeza 50 e
         tensiones-de-fases es no-semejantes com certeza 50 e tarea es medir-las-tensiones-de-cada fase)
         (porque "porque no se han medido las tensiones de cada fase"))

  (regra (si tension-en-empalme es .)
         (entonces tension-en-empalme es BT com certeza 100 e tarea es investigar-cual-es-la-tension-del-empalme e tension-em-empalme es AT com certeza 20)
         (porque "porque no se ha verificado la tensión del empalme"))

  (regra (si fases-en-empalme es .)
         (entonces fases-en-empalme es trifasico com certeza 20 e fases-en-empalme es monofasico com certeza 90 e tarea es investigar-cuales-son-las-fases-del-empalme )
         (porque "porque no se ha verificado el número de fases del empalme, se asume trifásico con una probablidad pequeña"))

 
  (regra (si regimen-neutro es .)
         (entonces regimen-neutro es TT com certeza 80 e regimen-neutro es TN com certeza 20 e tarea es investigar-cual-regimen-de-neutro-esta-implementonces)
         (porque "porque no se ha verificado el régimen de neutro y TT es mucho más frecuente "))

  (regra (si neutro es .)
         (entonces neutro es cortado com certeza 50 e neutro es no-cortado com certeza 50 e tarea es investigar-si-el-neutro-esta-cortado)
         (porque "porque no se ha verificado el corte del neutro"))


  (regra (si intensidad-general-de-fases es .)
         (entonces fases es desequilibradas com certeza 50 e fases es equilibradas com certeza 50 e tarea es medir-las-intensidades-de-cada-fase-en-carga)
         (porque "porque no se han medido las corrientes en cada fase"))

  (regra (si fases-de-iluminacion es .)
         (entonces fases-de-iluminacion es luminarias-alternadas com certeza 50 e fases-de-iluminacion es luminarias-no-alternadas com certeza 50 e tarea es investigar-como-estan-conectadas-las-luminarias )
         (porque "porque no se ha verificado la disposición alternada de las luminarias"))

  (regra (si puesta-a-tierra es .)
         (entonces puesta-a-tierra es existente com certeza 50 e puesta-a-tierra es inexistente com certeza 50 e  tarea es puesta-a-tierra)
          (porque "porque no se ha verificado la puesta a tierra de proteccion"))

  (regra (si diferencial-doble-polo es .)
         (entonces diferencial-doble-polo es existente com certeza 50 e diferencial-doble-polo es inexistente com certeza 50 e tarea es diferencial-doble-polo)
         (porque "porque no se ha verificado la presencia de diferencial-doble-polos"))

  (regra (si union-proteccion-y-neutro-en-empalme es .)
         (entonces union-proteccion-y-neutro-en-empalme es existente com certeza 50 e union-proteccion-y-neutro-en-empalme es inexistente com certeza 50 e tarea es union-proteccion-y-neutro-en-empalme)
         (porque "porque no se ha verificado la unión del conductor de protección y el conductor neutro en el empalme"))

)
  
   
;;***************************************
;;* REGLAS DE ENCADEAMENTO DE PERGUNTAS *
;;***************************************
                     
(defmodule REGLAS-PERGUNTAS (import MAIN ?ALL) 
                            (export ?ALL) 
                            (import REGLAS ?ALL)
                            (import PERCORRER-ARVORE ?ALL))
 
 (deftemplate REGLAS-PERGUNTAS::pergunta
   (slot atributo (default ?NONE))
   (slot a-pergunta (default ?NONE))
   (multislot respostas-validas (default ?NONE))
   (slot respondida (default FALSE))
   (multislot antecedentes (default ?DERIVE))
   (slot porque-titulo (default ?NONE))
   (slot unidad)
   (slot porque (default ?NONE)))
   
 ; regras para saida forcada de usuario
  (defrule REGLAS-PERGUNTAS::sairkII ( sair) ?rem <- (pergunta (atributo  ?onome)) => (retract ?rem))


 ;esta modificação permite seguir no questionario ainda que o usuario nao possa responder 
 ;O usuario deve responder com . quando não souber a resposta

 ;Esta aproximación es peligrosa en electricidad 
 (defrule REGLAS-PERGUNTAS::nebulizar-uma-resposta-nula
    (declare (salience 100))
    (no usar)
    ?f <- (regra (certeza ?c1) 
                 (si ?atributo es . $?rest))
    ?f2<-(atributo (nome ?atributo) 
                   (valor .) 
                   (certeza ?c2))  
    ?f3<-(pergunta (respostas-validas $?resposta) 
                   (atributo ?atributo)
                   (respondida TRUE))
    =>
    (while (> (length$ ?resposta) 0) 
                          do 
                          ; (printout t ?resposta)
                          (bind ?ovalor (nth 1 ?resposta))
                          (if (and (not (eq ?ovalor .)) (not (eq ?ovalor "?"))     )  then 
                                       (assert (atributo (nome ?atributo)
                                                         (valor ?ovalor)
                                                         (certeza 20))))
                          (bind ?resposta (rest$ ?resposta)) )     
    (retract ?f2))


  ;estas regras são disparadas quando o usuário tecla ?
  ;esta ajuda diz quais são as possíveis respostas
 (defrule REGLAS-PERGUNTAS::ajuda1
      (declare (salience 100))
      ?f2<-(atributo (nome ?atributo) 
                     (valor "?") 
                     (certeza ?c2))  
      ?f3<-(pergunta (respostas-validas $?resposta) 
                     (atributo ?atributo)
                     (respondida TRUE))
      =>
      (printout t "Débese responder con una de las siguientes alternativas" crlf)
      (while (> (length$ ?resposta) 0) 
                            do 
                            (bind ?ovalor (nth 1 ?resposta))
                            (if (not (eq ?ovalor "?"))  
                            then (printout t "<" ?ovalor "> ") )
                            (bind ?resposta (rest$ ?resposta)) )     
      (printout t crlf)
      (modify ?f3 (respondida FALSE))
   ;   (retract ?f2)  
      )

 ;esta ajuda mostra os fatos já acontecidos
 (defrule REGLAS-PERGUNTAS::ajuda2
 (declare (salience 50))
    ?f <- (pergunta (respondida TRUE)
                    (atributo ?nome))
          (atributo (nome ?nome) 
                    (valor ?valor)
                    (certeza ?certeza))
         ?f3 <-(atributo 
                    (nome ?outro-nome)
                    (valor "?"))
   =>
  (printout t ?nome " es " ?valor " com certeza de " ?certeza crlf)
 ; (retract ?f3)
  )
 
 ;esta ajuda mostra alguma regra inminente no caminho que está sendo percorrido
 (defrule REGLAS-PERGUNTAS::ajuda3 
          (declare (salience 5))
          (regra (si ?oque $?si) (entonces $?resto-consequente))               
          (atributo (nome ?oque))
   ?f3<-  (atributo (valor "?"))
          =>
           (printout t "Si " ?oque " " (implode$ ?si) " entonces " (implode$ ?resto-consequente) crlf)
           (retract ?f3)
          )

; as perguntas sao feitas quando nao tem antecedentes. Perguntas com antecedentes sao
; feitas apos os antecedentes foram respondidos
 (defrule REGLAS-PERGUNTAS::fazer-uma-pergunta
   ?f <- (pergunta (respondida FALSE)
                   (antecedentes)
                   (a-pergunta ?a-pergunta)
                   (atributo ?o-atributo)
                   (respostas-validas $?respostas-validas)
                   (porque-titulo ?oporquetitulo)
                   (porque ?oporque)
		   (unidad ?unidad)
                   )
   =>
   (modify ?f (respondida TRUE))
   (bind ?aresposta (fazer-pergunta ?a-pergunta ?respostas-validas ?oporquetitulo ?oporque ?unidad ))
   (if (or (eq ?aresposta p) (eq ?aresposta f)) then (assert (sair)))
   (assert (atributo (nome ?o-atributo)
                     (valor ?aresposta)
		     (unidad ?unidad)
		     )))
 
                      
;encadeamento forward nas perguntas 
 (defrule REGLAS-PERGUNTAS::pergunta-anterior-e-satisfeita
   ?f <- (pergunta (respondida FALSE)
                   (antecedentes ?nome es ?valor $?rest))
         (atributo (nome ?nome) 
	           (valor ?valor)
		   )
   =>
   (if (eq (nth 1 ?rest) e) 
    then (modify ?f (antecedentes 
                    (rest$ ?rest)))
    else (modify ?f (antecedentes ?rest))))                     
                      
                      
;encadeamento forward nas perguntas 
 (defrule REGLAS-PERGUNTAS::pergunta-anterior-NAO-EH-satisfeita
   ?f <- (pergunta (respondida FALSE)
                   (antecedentes ?nome no-es ?valor $?rest))
         (atributo (nome ?nome)
                   (valor ~?valor))
   =>
   (if   (eq (nth 1 ?rest) e) 
    then (modify ?f (antecedentes 
                    (rest$ ?rest)))
    else (modify ?f (antecedentes ?rest))))

;Automáticamente asigna trifasico al empalme cuando es Alta Tensión
  (defrule REGLAS-PERGUNTAS::empalme-AT-es-trifasico
       (atributo (nome tension-en-empalme) (valor AT))
  =>
     (assert
       (atributo (nome fases-en-empalme)  (valor trifasico))
  ))


;;**********************
;;* PERGUNTAS INICIAIS *
;;**********************

(defmodule PERGUNTAS-INICIAIS (import REGLAS-PERGUNTAS ?ALL))
 (deffacts PERGUNTAS-INICIAIS::pergunta-atributos


  (pergunta (atributo tierra-de-servicio )
            
            (a-pergunta "Verifique que el neutro de la instalación eléctrica esté puesto a tierra <existente> <inexistente>")
	    (porque-titulo "Tierra de Servicio")
	    (porque "La puesta a tierra de protección del neutro en la Instalación Eléctrica del cliente se denomina Tierra de Servicio y es un garantía de que el neutro estará a tierra independientemente de que la red de distribución tengan otras tierras de servicio en sus postes. Al tener el neutro conectado a tierra, el diferencial, puede tener mayor precisión para detectar desequilibrios en las corrintes de entrada y de salida, que es su principio de funcionamiento. Así que la normativa eléctrica exige especialmente este punto: El neutro debe ser conectado a tierra antes del diferencial. La puesta a tierra del neutro sirve para superar la situación de corte del neutro aprovechando que la energía eléctrica del neutro de la red de distribución llegue al neutro de la instalación del cliente, lo que es una solución temporal que mantendría la entrega de energía.")
	    (respostas-validas existente inexistente . "?")
	    )


  (pergunta (atributo conexion-a-plomeria )
            (antecedentes puesta-a-tierra es inexistente)
            (a-pergunta "Verifique que el cable de protección esté conectado a la plomería <conectado> o <no-conectado>")
            (porque-titulo "Conexión a Plomería")
            (porque "porque el diferencial se disparará aún cuando el circuito de falla sea efectivo a través de la plomería")
            (respostas-validas conectado no-conectado . "?")
            )

  (pergunta (atributo resistencia-de-tierra )
            (antecedentes puesta-a-tierra es existente)
            (a-pergunta "Mida la resistencia del Lazo de Tierra usando una telurómetro de pinza, introduzca el valor en ohm")
            (porque-titulo "Resistencia de Lazo de Tierra ")
            (porque "La Resistencia del Lazo de Tierra, que se mide con un telurómetro de piza, caracteriza la Resistencia del Circuito de Falla, que es un trayecto eléctrico temporal que se establece solo cuando courre una falla de aislamiento, porque ambos incluyen la Resistencia de la Puesta a Tierra, la cual es muy grande comparadas con los otros componentes de ambos circuitos. Así que esa apreciación permite asumir que las tres definiciones son esencialmente iguales cuando se usan para evaluar fallas a tierra. La Resistencia de la Puesta a Tierra es exactamente la oposición al paso de la corriente eléctrica que ofrece un dado mecanismo de puesta a tierra, piense en una pica clavada en el suelo o  en una malla de tierra. La Resistencia de la Puesta a Tierra se puede medir directamente, pero eso requiere desconectar el cable de protección, lo que se considera un riesgo innecesario cuando se dispone de telurómetros de pinza que pueden hacer la medicioń del lazo de tierra estando la instalación eléctrica en pleno funcionamiento")
            (respostas-validas entero)
	    (unidad "ohm")
            )

  (pergunta (atributo tension-de-seguridad )
            (a-pergunta "Cuál es el valor de la tensión de seguridad para su caso")
            (porque-titulo "Tensión de Seguridad")
            (porque "La tensión de seguridad se define en base a si el ambiente es húmedo (24V) o seco (50V). Es importante para estimar el riesgo de contacto indirecto.")
            (unidad "V")
            (respostas-validas entero)
            )

  (pergunta (atributo sensibilidad-diferencial)
            (antecedentes diferencial-doble-polo es existente)
            (a-pergunta "Digite la sensibilidad en miliAmperes del diferencial-doble-polo")
            (porque-titulo "Sensibilidad de Diferencial")
            (unidad "mA")
            (porque "La sensibilidad del diferencial indica cuánto el diferencial limitará la corriente de falla.")
            (respostas-validas entero)
            )


  (pergunta (atributo demora-de-diferencial)
            (antecedentes diferencial-doble-polo es existente)
            (a-pergunta "Digite la demora de disparo del diferencial en milisegundos")
            (porque-titulo "Demora de Diferencial")
            (unidad "ms")
            (porque "La rapidez con que se dispara el diferencial es importante para evitar daños a las personas ")
            (respostas-validas entero)
            )



  (pergunta (atributo tensiones-de-fases)
            (antecedentes fases-en-empalme es trifasico)
            (a-pergunta "Mida las tensiones de cada fase y verifique no estén más alejadas que un 3 a 4% son <semejantes> o <no-semejantes> ? ")
            (porque-titulo "Simultaneidad de funcionamiento de las cargas ?] ")
            (porque "porque de esta forma, se permite que las intensidades de cada carga estarán iguales")
            (respostas-validas semejantes no-semejantes . "?")
            )

  (pergunta (atributo union-de-proteccion-y-neutro-en-empalme)
            (antecedentes tarea es unir-proteccion-y-neutro-en-empalme)
            (a-pergunta "Verifique que haya unión entre el conductor de protección  y el conductor de neutro en el empalme <existente> o <inexistente> ? ")
            (porque-titulo "Unión de Protección y Neutro en el Empalme")
            (porque "porque es la recomendación de la SEC del lugar para efectuar la Neutralización")
            (respostas-validas existente inexistente . "?")
            )

  (pergunta (atributo fases-de-enchufes)
            (antecedentes intensidad-general-de-fases es equilibradas)
            (a-pergunta "Verifique si los circuitos de enchufes están dispuestos en una trenza alternando los enchufes de cada fase <enchufes-alternados> o <enchufes-no-alternados> ? ")
            (porque-titulo "Simultaneidad de funcionamiento de las cargas ?] ")
            (porque "porque de esta forma, las intensidades de cada carga estarán iguales")
            (respostas-validas enchufes-alternados enchufes-no-alternados . "?")
	    )

  (pergunta (atributo fases-de-iluminacion)
            (antecedentes intensidad-general-de-fases es equilibradas)
            (a-pergunta "Verifique si los circuitos de iluminación están dispuestos en una trenza alternando las luminarias de cada fase <luminarias-alternadas> o <luminarias-no-alternadas> ? ")
            (porque-titulo "Simultaneidad de funcionamiento de las cargas ?] ")
            (porque "porque de esta forma, las intensidades de cada carga estarán iguales")
            (respostas-validas luminarias-alternadas luminarias-no-alternadas . "?")
	    )

  (pergunta (atributo diferencial-doble-polo)
            ;(antecedentes puesta-a-tierra es existente)
            (a-pergunta "Verifique si hay diferencial-doble-polo instalado <existente> o no <inexistente> ? ")
            (porque-titulo "Diferencial ")
            (porque "Se debe usar diferenciales en cualquier sistema de combate contra contactos indirectos porque así lo recomienda la normativa eléctrica, debido a que limita el tiempo y la corriente de falla y mantiene segura la tensión de los equipos. Esta función es complementaria e independiente a la de otros sistemas de combate a los contactos directos y resiste al corte de neutro y a la degradación del sistema de puesta a tierra. Necesita la existencia de un camino de retorno de la energía de falla, para que el desequilibrio resultante pueda ser usado para disparar el diferencial. Así que que no funcionará si no hay puesta a tierra. El diferencial debe ser de doble polo para que corte el neutro en caso de falla, eso es exigido especialmente en la normativa. Es más seguro desconectar totalmente la instalación eléctrica (desconectando las fases y el neutro) debido a que de esta forma se evita la entrada de sobretensiones externas.")
            (respostas-validas existente inexistente . "?")
	    )

  (pergunta (atributo puesta-a-tierra)
            (antecedentes regimen-neutro es TT)
            (a-pergunta "Verifique si se ha instalado la puesta a tierra de protección <existente> o <inexistente> ? ")
            (porque-titulo "Puesta a Tierra de Protección")
            (porque "En régimen de neutro TT, se necesita instalar un sistema de puesta a tierra de protección porque esa es la forma en que la energía que se liberara durante una posible falla de aislamiento, será conducida a la tierra geológica.")
            (respostas-validas existente inexistente . "?")
            )


  (pergunta (atributo neutralizacion)
            (antecedentes regimen-neutro es TN)
            (a-pergunta "Verifique si los masas de los equipos serán conectadas al neutro en caso de falla. Esto es, si la neutralización es <existente> o <inexistente> ? ")
            (porque-titulo "Neutralización")
            (porque "Lo SEC orden hacer neutralización en regímenes TN")
            (respostas-validas existente inexistente . "?")
            )


  (pergunta (atributo intensidad-general-de-fases)
            (antecedentes fases-en-empalme es trifasico)
            (a-pergunta "Mida si las intensidades de las fases están <desequilibradas> <equilibradas> ?")
            (respostas-validas desequilibradas equilibradas . "?")
            (porque-titulo "Fases Desequilibradas")
            (porque  "Las fases desequilibradas pueden provocar tensiones peligrosas"  )
            )

  (pergunta (atributo tension-en-empalme)
            (a-pergunta "El empalme es <BT> o <AT>> ?")
	    (respostas-validas BT AT . "?")
	    (porque-titulo "Tensión en el Empalme ")
	    (porque  "Seleccione BT: Baja Tensión, o AT: Empalme en Alta Tensión. El empalme es la forma en que la empresa distribuidora de electricidad se conecta a la instalación eléctrica de un particular.Los empalmes de Alta Tensión son empleados cuando el consumo de electricidad es muy grande, debido a que es más económico usar alta tensión en esos casos. En los clientes que consumen poco, se usa baja tensión para evitar riesgos innecesarios." )
	    )

  (pergunta (atributo fases-en-empalme)
            (antecedentes tension-en-empalme es BT)
            (a-pergunta "El empalme es <monofasico> o <trifasico> ?")
            (respostas-validas monofasico trifasico . "?")
            (porque-titulo "Fases en Empalmes de Baja Tensión")
            (porque  "Seleccione si el empalme es monofásico o trifásico. Los empalmes monofásicos se usan en instalaciones que consumen hasta 40-45 Amperes, dados por su corriente de servicio. Los empalmes trifásicos se usan mayormente en empresas, industrias y locales comerciales porque consumen más de 45 Amperes. Los empalmes trifásicos son un poco más complejos que los monofásicos porque se debe preserva un equilibrio entre las corrientes de cada fase, para evitar que surjan tensiones por encima de lo que soportan los equipos. Esta es una explicación de por qué en las instalaciones domésticas solo se usan empalmes monofásicos: sus equipos no son tan resistentes a sobretensiones como los industriales y entonces sus instalaciones eléctricas no necesitan mayormente protecciones contra sobretensión. Eso no significa que estas ocurran, pero solo ocurren en ocasión de fallas externas, como cuando un transformador de la distribuidora tiene problemas."  )
            )


  (pergunta (atributo clase)
            (a-pergunta "La clase de protección contra contactos indirectos es <A> <B> ?")
            (respostas-validas A B . "?")
            (porque-titulo "Clases de Protección Contra Contacto Indirecto")
            (porque "Porque la adopción de un tipo de clase de protección define la forma en que se combate el contacto con superficies que quedan energizadas en caso de falla. Las medidas de clase A son diferentes de las de clase B. Las de clase A son más preventivas que las de clase B. Las de clase B actúan a posteriori de la ocurrencia de la falla.")
            )

  (pergunta (atributo regimen-neutro)
            (antecedentes clase es B)
            (a-pergunta "El regimen de neutro es <TN> o <TT> ?")
	    (respostas-validas TN TT . "?")
	    (porque-titulo "Clase B")
	    (porque "Los sistemas Clase B deben definir cómo se han de conectar las carcazas de los equipos, cuando ocurra una falla de aislamiento en estos. La elección que debe hacerse es TN: se conectan al cable neutro o TT:se conectan a la tierra de protección.")
	    )

  (pergunta (atributo falla)
            (a-pergunta "Elija la falla que quiere evaluar <neutro-cortado> o <falla-de-aislamiento> ?")
            (respostas-validas neutro-cortado falla-de-aislamiento . "?")
            (porque-titulo "Corte de Neutro o Falla de Aislamiento")
            (porque "porque una instalación eléctrica, aunque esté en buen estado, debe tener precauciones adicionales para evitar que los equipos que se conectan a ella puedan roducir sobretensiones peligrosas cuando fallen sus aislaciones o cuando se corte el conductor de neutro, el que llega desde el transformador de la empresa distribuidora eléctrica.")
            )
  )

 

;;*******************************************************
;;* REGLAS PARA IMPRIMIR UMA TABELA com OS DIAGNOSTICOS *
;;*******************************************************




(defmodule IMPRIMIR (import MAIN ?ALL))

 ; este aqui elimina os diagnostico que tenham certeza menor que 20%
 ; pode ser desativado, la no começo com a bandera (eliminar-......._)
 (defrule IMPRIMIR::eliminar-diagnosticos-muito-inciertos ""
  (declare (salience 26)) ;un valor supeiror al de imprimr diagnosticos
  (eliminar-diagnosticos-pouco-fundados)
  ?rem <- (atributo (nome diagnostico)
           (valor   ?valor)
	   (porque ?porque)
           (certeza ?per&:(< ?per 20)))
  =>
  (format t "%n %n %n ################# %n # Eliminado el diagnostico  %-24s, %-24s porque se lo cree poco. La creencia es de %-2d. %n################# %n" ?valor ?porque ?per )
  (retract ?rem))


(defrule IMPRIMIR::sair
   (declare (salience 5000))
   (atributo (valor p))
   =>
   (assert (sair)))


 ; esta regra garante alguma informação quando não houver diagnósticos possíveis
 (defrule IMPRIMIR::nao-ha-diagnostico
   (declare (salience 100))
   (not (imprimir))
   (not (atributo (nome diagnostico)))
   =>
   (assert (atributo (nome diagnostico) 
                     (valor "No hay diagnóstico")
                     (certeza 100)
                     (porque "No hay suficientes evidencias"))))

 ; este aqui imprimir os títulos
 (defrule IMPRIMIR::titulos ""
   (declare (salience 10))
   (not (sair))
   
   =>
   (printout t t crlf crlf)   
   (printout t " Evaluación de Riesgos Eléctricos por Contactos Indirectos   " t t)
   (printout t " Situación de Riesgo          Creencia  Justificación del Experto  " t)
   (printout t "----------------------------------------------------------" t)
   (assert (imprimir)))

;abrir archivo
 (defrule IMPRIMIR::initial-facts

  =>
   (open "archivo.facts" archivo_id)
   (printout archivo_id "prueba")
   (close archivo_id)
 )

;imprimir a un archivos
 (defrule IMPRIMIR::imprimir-a-archivo
   (declare (salience 9))
   (atributo (nome ?nome))

  =>
;   (format archivo_id " %" ?nome)
 )

 ;este aqui cassa com cada atributo de diagnostico e imprime os campos na tabela
 (defrule IMPRIMIR::imprimir-diagnostico ""
 (declare (salience 9))
  (not (sair))
  ?rem <- (atributo (nome diagnostico) 
                    (valor ?nome&:(neq ?nome tarea)) 
                    (certeza ?per)
                    (porque ?porque))             
  (not (atributo (nome diagnostico) 
                 (certeza ?per1&:(> ?per1 ?per))))
  =>
  (retract ?rem)
  (format t "  %-24s %2d%%  %-80s %n%n" ?nome ?per ?porque))
  

 ;este se eliminan los hechos que generan las preguntas cuando el cliente responde con .
 (defrule IMPRIMIR::eliminar-hechos-. ""
 (declare (salience 9))
  ?rem <- (atributo (valor .))
  =>
  (retract ?rem)
 )


 
 ;este aqui fecha a tabela de diagnosticos e abre a de fatos que foram consultados para o diagnostico
 ;foi sugestão do Gilson
 (defrule IMPRIMIR::cerrar-tabela ""
     (declare (salience 7))
     (not (sair))
     (not (atributo (nome diagnostico)))
     =>
     (printout t crlf crlf "Inferencias que soportan lo(s) diagnóstico(s) " crlf)        
     (printout t " Inferencia                Valor                  Creencia Justificación" crlf)
     (printout t "--------------------------------------------------------" crlf))


 ;este aqui imprime os fatos que foram consultados
 (defrule IMPRIMIR::imprimir-inferencias ""
  (declare (salience 6))
  (not (sair))
   ?rem <- (atributo (nome ?onome&:(neq ?onome tarea)) 
                     (valor ?ovalor&:(neq ?ovalor f)) 
                     (certeza ?per)
		     (porque ?rest)
		     )
   =>
   (retract ?rem)
   (if (numberp ?ovalor)
    then
   (format t "  %-24s %-24d%  2d%% %-10s %n" ?onome ?ovalor ?per ?rest)
    else
   (format t "  %-24s %-24s%  2d%% %-10s %n" ?onome ?ovalor ?per ?rest)
   )
   )
   

 ;este aqui fecha a tabela de fatos
 (defrule IMPRIMIR::fatos-tabela ""
     (declare (salience 5))
     (not (sair))
     (not (atributo (nome diagnostico)))
     =>
     (printout t crlf crlf "Hechos que justifican el diagnóstico " crlf)
     (printout t " Hechos                  Valor                  Creencia Justificación" crlf)
     (printout t "--------------------------------------------------------" crlf))


 ;este aqui imprime os fatos que foram consultados
 (defrule IMPRIMIR::imprimir-medidas ""
   (declare (salience 4))
   (not (sair))
   ?rem <- (atributo (nome ?onome&:(neq ?onome tarea))
                     (valor ?valor&:(numberp ?valor))
                     (unidad ?unidad)
                     (certeza ?per)
                     )
   =>
   (retract ?rem)
   (format t "  %-24s %d %-20s %d%% porque fueron ingresadas como medicioness %n" ?onome ?valor ?unidad ?per))




 ;este aqui imprime os fatos que foram consultados
 (defrule IMPRIMIR::imprimir-fatos ""
  (declare (salience 4))
  (not (sair))
   ?rem <- (atributo (nome ?onome&:(neq ?onome tarea))
                     (valor ?valor&:(not (numberp ?valor)))
                     (certeza ?per)
                     )
   =>
   (retract ?rem)
   (format t "  %-24s %-24s %d%% porque fue respondido en cuestionario %n" ?onome ?valor ?per ))


;este aqui imprime os fatos que foram consultados
 (defrule IMPRIMIR::imprimir-observaciones ""
  (declare (salience 3))
  (not (sair))
   ?rem <- (atributo (nome ?onome&:(neq ?onome tarea))
                     (valor ?ovalor&:(not (numberp ?ovalor)))
                     (certeza ?per)
                     )
   =>
   (retract ?rem)
   (format t "  %-24s  %-12s Observado en visita técnica %n" ?onome ?ovalor))


 ; se eliminan las tareas cumplidas
 (defrule IMPRIMIR::eliminar-tareas-materializadas ""
  (declare (salience 5))
  ?rem <- (atributo (nome tarea) (valor ?valor))
          (atributo (nome ?valor) (valor existente))
          (not (atributo (nome ?valor) (valor inexistente)))
  =>
 ; (format t "%n %n %n ################# %n # Eliminada la tarea  %-24s porque ya se ha materializado su objetivo. %n################# %n" ?valor)
  (retract ?rem))




 ;este aqui fecha a tabela de diagnosticos e abre a de fatos que foram consultados para o diagnostico
 ;foi sugestão do Gilson
 (defrule IMPRIMIR::tareas-pendientes-titulo 
     (declare (salience 2))
     (not (sair))
     (not (atributo (nome diagnostico)))
     =>
     (printout t crlf crlf "Tareas Pendientes que Buscan Compensar los Riesgos de Contacto Indirecto " crlf)
     (printout t " Tarea                        Creencia Justificación" crlf)
     (printout t "--------------------------------------------------------" crlf))


 ;este aqui imprime os fatos que foram consultados
 (defrule IMPRIMIR::tareas-pendientes ""
  (declare (salience 1))
  (not (sair))
   ?rem <- (atributo (nome ?onome&:(eq ?onome tarea))
                     (valor ?ovalor)
                     (porque ?porque)
                     )
   =>
   (retract ?rem)
   (if (not (eq ?ovalor f)) then
   (format t "Entregue un presupuesto para %-2s %-2s %n" ?ovalor ?porque )))



 ;este es o fim, começamos de novo?
 (defrule IMPRIMIR::fim
  (not (atributo (nome diagnostico)))
  =>
;  (close archivo_id)
  (printout t crlf crlf "Digite uma letra e presione ENTER para concluir esta sesión de trabajo y comenzar otra" crlf "**   ")
  (read)
  (printout t crlf crlf)
  (reset)
  (run))



