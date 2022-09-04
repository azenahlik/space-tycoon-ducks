rm -rf space_tycoon_generated_client

docker-compose run swagger-client-gen

chmod -R a+rw space_tycoon_generated_client
