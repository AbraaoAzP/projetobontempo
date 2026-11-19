// List specialty records
query especialidades verb=GET {
  api_group = "Especialidades"

  input {
  }

  stack {
    db.query especialidade {
      sort = {nome: "asc"}
      return = {type: "list"}
    } as $especialidades
  }

  response = $especialidades|map:{
    id: $$.id
    nome: $$.nome
  }
}
