#######
Clients
#######

curl
====

Test Custodia::

    $ curl --unix-socket /var/run/custodia.sock -X GET http://localhost/
    {"message": "Quis custodiet ipsos custodes?"}

Initialize a container for secrets::

    $ curl --unix-socket /var/run/custodia.sock -X POST http://localhost/secrets/container/

Create or update a secret::

    $ curl --unix-socket /var/run/custodia.sock -H "Content-Type: application/json" -X PUT http://localhost/secrets/container/key -d '{"type": "simple", "value": "secret value"}'

Get a secret::

    $ curl --unix-socket /var/run/custodia.sock -X GET http://localhost/secrets/container/key
    {"type":"simple","value":"secret value"}

Delete a secret::

    $ curl --unix-socket /var/run/custodia.sock -X DELETE http://localhost/secrets/container/key
