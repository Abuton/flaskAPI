app_name = bank-employee-api

build:
	docker build -t $(app_name)

run:
	docker run --name $(app_name) --detach -p 8080:8080 $(app_name)

kill:
	docker stop $(app_name)
	docker container prune -f
	docker rmi -f $(app_name)