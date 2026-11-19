// Update specialty record
query "especialidade/{especialidade_id}" verb=PATCH {
  api_group = "Especialidades"

  input {
    int especialidade_id filters=min:1
    text nome? filters=trim
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

    var $especialidade_atualizada {
      value = $especialidade
    }

    conditional {
      if ($input.nome != null) {
        precondition ($input.nome != "") {
          error_type = "inputerror"
          error = "Nome da especialidade não pode estar vazio."
        }

        var $nome_normalizado {
          value = $input.nome|to_lower
        }

        db.query especialidade {
          where = ($db.especialidade.nome_normalizado == $nome_normalizado) && ($db.especialidade.id != $input.especialidade_id)
          return = {type: "single"}
        } as $especialidade_existente

        precondition ($especialidade_existente == null) {
          error_type = "inputerror"
          error = "Já existe uma especialidade com esse nome."
        }

        db.patch especialidade {
          field_name = "id"
          field_value = $input.especialidade_id
          data = {
            nome: $input.nome
            nome_normalizado: $nome_normalizado
          }
        } as $especialidade_atualizada
      }
    }
  }

  response = {
    id: $especialidade_atualizada.id
    nome: $especialidade_atualizada.nome
  }
}
