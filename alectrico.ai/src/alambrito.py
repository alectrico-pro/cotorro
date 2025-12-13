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

