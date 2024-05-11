# MongoDB: Um Banco de Dados NoSQL

O MongoDB é um banco de dados NoSQL, ou seja, não relacional, que armazena dados em formato de documentos flexíveis similares a JSON com campos chave-valor. Ele é projetado para lidar com volumes de dados variados e pode ser escalado horizontalmente com facilidade.

## Características Principais:
- **Documentos Flexíveis:** Os dados são armazenados em documentos JSON-like, o que permite uma modelagem de dados mais flexível em comparação com bancos de dados relacionais.
- **Escalabilidade Horizontal:** O MongoDB pode ser facilmente escalado horizontalmente, distribuindo dados em vários servidores para lidar com volumes crescentes de dados.
- **Alta Disponibilidade:** Suporta replicação automática e failover para garantir alta disponibilidade e tolerância a falhas.
- **Consultas Poderosas:** Oferece suporte a consultas complexas, incluindo agregação, indexação e pesquisa geoespacial.

# MongoDB Express

O MongoDB Express é uma interface web para gerenciar bancos de dados MongoDB de forma visual. Ele fornece uma maneira conveniente de interagir com suas coleções de dados, executar consultas, adicionar, editar e excluir documentos, entre outras operações, tudo através de uma interface amigável baseada em navegador.

## Como Criar um Banco de Dados e um Esquema no MongoDB Express:

1. **Acesso à Interface Web:**
   - Abra um navegador da web e navegue até `http://localhost:8081` (ou o endereço e porta que você especificou durante a execução).

2. **Criação de Banco de Dados:**
   - Na interface do `mongodb_express`, você verá uma lista de bancos de dados existentes (se houver). Para criar um novo banco de dados, clique no botão "Add Database".
   - Insira o nome do novo banco de dados e clique em "Create".

3. **Criação de Esquema:**
   - Dentro do banco de dados recém-criado, clique no botão "Add Collection" para adicionar uma nova coleção (esquema).
   - Insira o nome da coleção e clique em "Create".
   - Agora você pode definir os campos e tipos de dados para o esquema da coleção usando a interface.

4. **Operações de Dados:**
   - Depois de criar o esquema, você pode adicionar, editar e excluir documentos diretamente na interface do `mongodb_express`.
   - Você também pode executar consultas e outras operações de banco de dados usando a funcionalidade fornecida.

O MongoDB Express é uma ferramenta útil para desenvolvedores e administradores de banco de dados que desejam interagir com o MongoDB de forma visual e conveniente, sem precisar usar a linha de comando ou outras ferramentas de gerenciamento de banco de dados.

## Tutorial: Criando um Usuário no MongoDB em um Ambiente Docker

1. Acesse o container do mongodb:

```
docker exec -it mmongoDB mongo
```

2. No shell do MongoDB, use o comando "use nome_do_seu_banco" para selecionar o banco de dados "nome_do_seu_banco".

3. Em seguida, use o comando db.createUser para criar um novo usuário com as permissões necessárias. Por exemplo:

```
db.createUser({
    user: 'seu_user',
    pwd: 'sua_senha',
    roles: [{ role: 'readWrite', db: 'seu_banco' }]
})
```

Lembre-se de substituir as credenciais e o nome do banco de dados conforme necessário para atender aos requisitos do seu aplicativo.

