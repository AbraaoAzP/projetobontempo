// Delete professional record
query "profissional/{profissional_id}" verb=DELETE {
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

    db.del profissional {
      field_name = "id"
      field_value = $input.profissional_id
    }
  }

  response = {success: true}
  guid = "N1wZjKbJk37rAyBMkkpNmJypqgg"
}
