// Create specialty record
query especialidades verb=POST {
  api_group = "Especialidades"

  input {
    text nome filters=trim
  }

  stack {
    precondition ($input.nome != "") {
      error_type = "inputerror"
      error = "Nome da especialidade é obrigatório."
    }

    var $nome_normalizado {
      value = $input.nome|to_lower
    }

    db.query especialidade {
      where = $db.especialidade.nome_normalizado == $nome_normalizado
      return = {type: "single"}
    } as $especialidade_existente

    precondition ($especialidade_existente == null) {
      error_type = "inputerror"
      error = "Já existe uma especialidade com esse nome."
    }

    db.add especialidade {
      data = {
        nome: $input.nome
        nome_normalizado: $nome_normalizado
      }
    } as $especialidade
  }

  response = {
    id: $especialidade.id
    nome: $especialidade.nome
  }
}
