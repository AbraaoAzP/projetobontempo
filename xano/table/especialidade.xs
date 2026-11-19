// Especialidades
table especialidade {
  auth = false

  schema {
    int id
    text nome filters=trim
    text nome_normalizado filters=trim|lower
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "nome_normalizado"}]}
  ]
}
