// Get professional record
query "profissional/{profissional_id}" verb=GET {
  api_group = "Profissionais"

  input {
    int profissional_id filters=min:1
  }

  stack {
    db.get profissional {
      field_name = "id"
      field_value = $input.profissional_id
    } as $profissional

    precondition ($profissional != null) {
      error_type = "notfound"
      error = "Profissional não encontrado."
    }
  }

  response = {
    id: $profissional.id
    nome: $profissional.nome
    telefone: $profissional.telefone
    email: $profissional.email
    especialidade: $profissional.especialidade
  }
  guid = "zOOMTb0_lq2JNk3tNpBYLkr2UoE"
}
