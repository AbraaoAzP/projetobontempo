// Get specialty record
query "especialidade/{especialidade_id}" verb=GET {
  api_group = "Especialidades"

  input {
    int especialidade_id filters=min:1
  }

  stack {
    db.get especialidade {
      field_name = "id"
      field_value = $input.especialidade_id
    } as $especialidade

    precondition ($especialidade != null) {
      error_type = "notfound"
      error = "Especialidade não encontrada."
    }
  }

  response = {
    id: $especialidade.id
    nome: $especialidade.nome
  }
}
