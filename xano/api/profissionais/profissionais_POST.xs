// Create professional record
query profissionais verb=POST {
  api_group = "Profissionais"

  input {
    text nome filters=trim
    text telefone? filters=trim
    email email? filters=trim
    text especialidade? filters=trim
  }

  stack {
    precondition ($input.nome != "") {
      error_type = "inputerror"
      error = "Nome é obrigatório."
    }

    function.run "validar_telefone_paciente" {
      input = {telefone: $input.telefone}
    } as $telefone_validado

    precondition ($telefone_validado.valid) {
      error_type = "inputerror"
      error = "Telefone inválido."
    }

    db.add profissional {
      data = {
        nome: $input.nome
        telefone: $input.telefone
        email: $input.email
        especialidade: $input.especialidade
      }
    } as $profissional
  }

  response = {
    id: $profissional.id
    nome: $profissional.nome
    telefone: $profissional.telefone
    email: $profissional.email
    especialidade: $profissional.especialidade
  }
}
