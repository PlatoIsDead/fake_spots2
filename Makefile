set_env:
	pyenv virtualenv 3.12.9 fake_spots_env
	pyenv local fake_spots_env

reinstall_package:
	@pip uninstall -y fsp || :
	@pip install -e .

set_reqs:
	python -m pip install --upgrade pip
	@pip install -r requirements.txt

run_tests:
	python test/super_test.py

install_docker:
	docker build -t api/api .

run_docker:
	docker run -p 8080:8000 api

run_api:
	uvicorn api.api:app --reload

deploy:
	@echo ">>> Creating Artifact Registry repository (if not exists)..."
	@gcloud artifacts repositories create $(DOCKER_REPO_NAME) --repository-format=docker \
		--location=$(GCP_REGION) --description="My first repository for storing Docker images in GAR" || true

	@echo ">>> Building Docker image..."
	@docker build --platform linux/amd64 -t $(IMAGE_URI) .

	@echo ">>> Pushing Docker image to Google Artifact Registry..."
	@docker push $(IMAGE_URI)

	@echo ">>> Deploying to Google Cloud Run with environment variables..."
	@gcloud run deploy $(DOCKER_IMAGE_NAME) --image $(IMAGE_URI) --region $(GCP_REGION) --quiet --env-vars-file .env.yaml
