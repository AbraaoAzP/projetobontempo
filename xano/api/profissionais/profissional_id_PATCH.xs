// Edit professional record
query "profissional/{profissional_id}" verb=PATCH {
  api_group = "Profissionais"

  input {
    int profissional_id filters=min:1
    text nome?="__xano_missing_nome_profissional_4bd7f28f__"
    text telefone?="__xano_missing_telefone_profissional_4bd7f28f__"
    email email?="missing-profissional-field-4bd7f28f@invalid.invalid"
    text especialidade?="__xano_missing_especialidade_profissional_4bd7f28f__"
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

    precondition (($input.nome == "__xano_missing_nome_profissional_4bd7f28f__") || ($input.nome == "") || (($input.nome != null) && (($input.nome|trim) != ""))) {
      error_type = "inputerror"
      error = "Nome não pode estar vazio."
    }

    conditional {
      if ($input.telefone != "__xano_missing_telefone_profissional_4bd7f28f__") {
        function.run "validar_telefone_paciente" {
          input = {telefone: $input.telefone}
        } as $telefone_validado

        precondition ($telefone_validado.valid) {
          error_type = "inputerror"
          error = "Telefone inválido."
        }
      }
    }

    var $updates {
      value = {}
    }

    conditional {
      if (($input.nome != "__xano_missing_nome_profissional_4bd7f28f__") && (($input.nome|trim) != "")) {
        var.update $updates.nome {
          value = $input.nome|trim
        }
      }
    }

    conditional {
      if (($input.telefone != "__xano_missing_telefone_profissional_4bd7f28f__") && (($input.telefone == null) || ($input.telefone == ""))) {
        var.update $updates.telefone {
          value = null
        }
      }
    }

    conditional {
      if (($input.telefone != "__xano_missing_telefone_profissional_4bd7f28f__") && ($input.telefone != null) && ($input.telefone != "")) {
        var.update $updates.telefone {
          value = $input.telefone
        }
      }
    }

    conditional {
      if (($input.email != "missing-profissional-field-4bd7f28f@invalid.invalid") && (($input.email == null) || ($input.email == ""))) {
        var.update $updates.email {
          value = null
        }
      }
    }

    conditional {
      if (($input.email != "missing-profissional-field-4bd7f28f@invalid.invalid") && ($input.email != null) && ($input.email != "")) {
        var.update $updates.email {
          value = $input.email
        }
      }
    }

    conditional {
      if (($input.especialidade != "__xano_missing_especialidade_profissional_4bd7f28f__") && (($input.especialidade == null) || ($input.especialidade == ""))) {
        var.update $updates.especialidade {
          value = null
        }
      }
    }

    conditional {
      if (($input.especialidade != "__xano_missing_especialidade_profissional_4bd7f28f__") && ($input.especialidade != null) && ($input.especialidade != "")) {
        var.update $updates.especialidade {
          value = $input.especialidade|trim
        }
      }
    }

    var $profissional_atualizado {
      value = $profissional
    }

    conditional {
      if (($updates|is_empty) == false) {
        db.patch profissional {
          field_name = "id"
          field_value = $input.profissional_id
          data = $updates
        } as $resultado_patch

        var.update $profissional_atualizado {
          value = $resultado_patch
        }
      }
    }
  }

  response = {
    id: $profissional_atualizado.id
    nome: $profissional_atualizado.nome
    telefone: $profissional_atualizado.telefone
    email: $profissional_atualizado.email
    especialidade: $profissional_atualizado.especialidade
  }
}
