// List professional records
query profissionais verb=GET {
  api_group = "Profissionais"

  input {
  }

  stack {
    db.query profissional {
      return = {type: "list"}
    } as $profissionais
  }

  response = $profissionais|map:{
    id: $$.id
    nome: $$.nome
    telefone: $$.telefone
    email: $$.email
    especialidade: $$.especialidade
  }
  guid = "xE_0xL897kQR0vQ35lPvgIoxm8w"
}
