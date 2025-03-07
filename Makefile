.PHONY: install run-dev docker-build docker-run docker-dev docker-stop docker-clean test deploy-ecr ecr-login ecr-create-repo ecr-push
run-dev:
	uv run src/app/app.py

docker-build:
	docker build -t $(ECR_REPOSITORY):$(IMAGE_TAG) -f src/app/Dockerfile .

docker-run:
	docker run -p 8000:8000 \
		--name fastapi-app \
		--rm \
		$(ECR_REPOSITORY):$(IMAGE_TAG) 

docker-dev: docker-stop docker-build docker-run

docker-stop:
	docker stop fastapi-app 2>/dev/null || true
	docker rm fastapi-app 2>/dev/null || true

docker-clean: docker-stop
	docker rmi $(ECR_REPOSITORY):$(IMAGE_TAG) || true

# AWS ECR commands
deploy-ecr: ecr-login ecr-create-repo ecr-push

# Docker and ECR variables
ECR_REPOSITORY=awscvgenerator
AWS_REGION=eu-north-1
IMAGE_TAG=latest

# Docker commands
docker-build:
	docker build -t $(ECR_REPOSITORY):$(IMAGE_TAG) -f src/app/Dockerfile .

# ECR commands
ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(shell aws sts get-caller-identity --query Account --output text).dkr.ecr.$(AWS_REGION).amazonaws.com

ecr-create-repo:
	aws ecr create-repository --repository-name $(ECR_REPOSITORY) --region $(AWS_REGION) || true

ecr-push: ecr-login ecr-create-repo
	docker tag $(ECR_REPOSITORY):$(IMAGE_TAG) $(shell aws sts get-caller-identity --query Account --output text).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPOSITORY):$(IMAGE_TAG)
	docker push $(shell aws sts get-caller-identity --query Account --output text).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPOSITORY):$(IMAGE_TAG)

# Help
help:
	@echo "=== FastAPI AWS Deployment ==="
	@echo ""
	@echo "Development Commands:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make run-dev      - Run development server"
	@echo "  make test         - Run tests"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make docker-dev   - Build and run Docker container"
	@echo "  make docker-stop  - Stop Docker container"
	@echo "  make docker-clean - Clean Docker resources"
	@echo ""
	@echo "AWS Commands:"
	@echo "  make deploy-ecr   - Build and push Docker image to ECR"